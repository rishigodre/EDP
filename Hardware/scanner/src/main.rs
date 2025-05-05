use std::io::{BufRead};
use std::time::Duration;
use std::{
    fs::File,
    io::BufReader,
};
use reqwest::Client;
use tokio;
use tokio::sync::mpsc;
use tokio::time::sleep;

//TODO: to be read from a config file, which can be updated server side
static HWID: &str = "9334de0b9ebd424d95e40d338953137e";
static HWPASS: &str = "A1B2C3D4E5F6G7H8";
static PIPE_PATH: &str = "/tmp/hw_data_pipe";

async fn pipe_in(tx: mpsc::Sender<String>) {
    println!("Starting pipe reader");
    loop {
        let file = File::open(PIPE_PATH).unwrap();
        let reader = BufReader::new(file);
        for line in reader.lines() {
            match line {
                Ok(data) => {
                    match tx.send(data).await {
                        Ok(data) => {}
                        Err(e) => {
                            eprintln!("Error {}", e)
                        }
                    }
                }
                Err(e) => {
                    eprintln!("Error reading from FIFO: {}", e);
                    sleep(Duration::from_secs(1)).await;
                }
            }
        }
    }
}

async fn create_and_upload_chunk(mut rx: mpsc::Receiver<String>) {
    println!("Starting Uploader");
    loop {
        let client = Client::new();
        let mut chunk = String::new();
        chunk.push_str(HWID);
        chunk.push_str(HWPASS);

        let mut lines = 0;
        loop {
            match rx.recv().await {
                Some(data) => {
                    chunk.push_str(data.as_str());
                    chunk.push_str("\n");
                    if lines > 10 {
                        lines = 0;
                        break;
                    }
                    lines += 1;
                }
                None => {
                    eprint!("Channel is closed");
                }
            }
        }
        // println!("Chunk => {}", chunk);
        let res = client
            .post("http://localhost:3000/api/addrawdata")
            .header("Content-Type", "text/plain")
            .body(chunk.clone())
            .timeout(Duration::from_secs(5))
            .send()
            .await;

        match res {
            Ok(res) => {
                if res.status().is_success() {
                    println!("Data successfully uploaded.");
                } else {
                    eprintln!("Server responded with error: {}", res.status());
                }
            }
            Err(e) => {
                eprintln!("Error in sending POST req: {}", e);
                sleep(Duration::from_secs(2)).await;
            }
        }
    }
}

#[tokio::main]
async fn main() {
    let (tx, rx) = mpsc::channel::<String>(64);
    println!("Starting scanner service on {}", PIPE_PATH);
    tokio::spawn(async move { pipe_in(tx).await });
    create_and_upload_chunk(rx).await
}
