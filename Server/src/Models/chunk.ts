// External dependencies
import { ObjectId } from "mongodb";
// Class Implementation
export default class Chunk {
    constructor(public data: string, public id?: ObjectId) {}
}