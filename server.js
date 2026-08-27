const express = require("express");
const mongoose = require("mongoose");

const app = express();
const PORT = 3000;

app.use(express.json());

mongoose.connect("mongodb://127.0.0.1:27017/nexus")
    .then(() => console.log("MongoDB connected successfully!"))
    .catch((err) => console.log("MongoDB connection error:", err));

const userSchema = new mongoose.Schema({
    name: String,
    project: String
});

const User = mongoose.model("User", userSchema);

// GET home
app.get("/", (req, res) => {
    res.json({
        message: "NEXUS API is running successfully!"
    });
});

// CREATE
app.post("/api/data", async (req, res) => {
    try {
        const user = await User.create(req.body);

        res.status(201).json({
            message: "Data saved successfully!",
            data: user
        });
    } catch (error) {
        res.status(500).json({
            message: "Error saving data",
            error: error.message
        });
    }
});

// READ
app.get("/api/data", async (req, res) => {
    try {
        const users = await User.find();

        res.json({
            message: "Data retrieved successfully!",
            data: users
        });
    } catch (error) {
        res.status(500).json({
            message: "Error retrieving data",
            error: error.message
        });
    }
});

// UPDATE
app.put("/api/data/:id", async (req, res) => {
    try {
        const updatedUser = await User.findByIdAndUpdate(
            req.params.id,
            req.body,
            { new: true }
        );

        res.json({
            message: "Data updated successfully!",
            data: updatedUser
        });
    } catch (error) {
        res.status(500).json({
            message: "Error updating data",
            error: error.message
        });
    }
});

// DELETE
app.delete("/api/data/:id", async (req, res) => {
    try {
        await User.findByIdAndDelete(req.params.id);

        res.json({
            message: "Data deleted successfully!"
        });
    } catch (error) {
        res.status(500).json({
            message: "Error deleting data",
            error: error.message
        });
    }
});

app.listen(PORT, () => {
    console.log(`NEXUS server running on http://localhost:${PORT}`);
});