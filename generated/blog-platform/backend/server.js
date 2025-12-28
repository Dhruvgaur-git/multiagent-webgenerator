require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { Pool } = require('pg');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = process.env.PORT || 5000;
const JWT_SECRET = process.env.JWT_SECRET || 'supersecretjwtkey'; // Use a strong secret in production
const saltRounds = 10; // For bcrypt hashing

// Middleware
app.use(cors());
app.use(express.json());

// PostgreSQL Connection Pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false // Required for Neon DB connection over SSL
  }
});

pool.on('error', (err) => {
  console.error('Unexpected error on idle client', err);
  process.exit(-1);
});

// Test DB connection
app.get('/api/health', async (req, res) => {
  try {
    await pool.query('SELECT NOW()');
    res.status(200).json({ message: 'Database connected successfully' });
  } catch (error) {
    console.error('Database connection error:', error.message);
    res.status(500).json({ message: 'Database connection failed', error: error.message });
  }
});

// JWT Authentication Middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (token == null) return res.sendStatus(401); // No token

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.sendStatus(403); // Invalid token
    req.user = user;
    next();
  });
};

// --- Auth Routes ---

// Register a new author/admin
app.post('/api/auth/register', async (req, res) => {
  const { username, password, role = 'author' } = req.body; // Default role to 'author'
  try {
    const hashedPassword = await bcrypt.hash(password, saltRounds);
    const result = await pool.query(
      'INSERT INTO users (username, password_hash, role) VALUES ($1, $2, $3) RETURNING id, username, role',
      [username, hashedPassword, role]
    );
    const user = result.rows[0];
    const token = jwt.sign({ id: user.id, username: user.username, role: user.role }, JWT_SECRET, { expiresIn: '1h' });
    res.status(201).json({ message: 'User registered successfully', token, user: { id: user.id, username: user.username, role: user.role } });
  } catch (error) {
    if (error.code === '23505') { // Unique violation error code
      return res.status(409).json({ message: 'Username already exists' });
    }
    console.error('Error during registration:', error.message);
    res.status(500).json({ message: 'Server error during registration' });
  }
});

// Login an author/admin
app.post('/api/auth/login', async (req, res) => {
  const { username, password } = req.body;
  try {
    const result = await pool.query('SELECT * FROM users WHERE username = $1', [username]);
    const user = result.rows[0];

    if (!user) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }

    const isPasswordValid = await bcrypt.compare(password, user.password_hash);
    if (!isPasswordValid) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }

    const token = jwt.sign({ id: user.id, username: user.username, role: user.role }, JWT_SECRET, { expiresIn: '1h' });
    res.status(200).json({ message: 'Logged in successfully', token, user: { id: user.id, username: user.username, role: user.role } });
  } catch (error) {
    console.error('Error during login:', error.message);
    res.status(500).json({ message: 'Server error during login' });
  }
});

// --- Blog Post CRUD --- 

// Create a new blog post (protected)
app.post('/api/posts', authenticateToken, async (req, res) => {
  const { title, content } = req.body;
  const author_id = req.user.id; // Get author ID from authenticated token

  if (!title || !content) {
    return res.status(400).json({ message: 'Title and content are required' });
  }

  try {
    const result = await pool.query(
      'INSERT INTO posts (title, content, author_id) VALUES ($1, $2, $3) RETURNING *',
      [title, content, author_id]
    );
    res.status(201).json(result.rows[0]);
  } catch (error) {
    console.error('Error creating post:', error.message);
    res.status(500).json({ message: 'Error creating post' });
  }
});

// Get all blog posts with pagination (public)
app.get('/api/posts', async (req, res) => {
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 10;
  const offset = (page - 1) * limit;

  try {
    const postsResult = await pool.query(
      `SELECT p.id, p.title, p.content, p.created_at, p.updated_at, u.username as author_username
       FROM posts p
       JOIN users u ON p.author_id = u.id
       ORDER BY p.created_at DESC
       LIMIT $1 OFFSET $2`,
      [limit, offset]
    );
    const totalPostsResult = await pool.query('SELECT COUNT(*) FROM posts');
    const totalPosts = parseInt(totalPostsResult.rows[0].count);
    const totalPages = Math.ceil(totalPosts / limit);

    res.status(200).json({
      posts: postsResult.rows,
      currentPage: page,
      totalPages: totalPages,
      totalPosts: totalPosts,
    });
  } catch (error) {
    console.error('Error getting posts:', error.message);
    res.status(500).json({ message: 'Error getting posts' });
  }
});

// Get a single blog post (public)
app.get('/api/posts/:id', async (req, res) => {
  const { id } = req.params;
  try {
    const postResult = await pool.query(
      `SELECT p.id, p.title, p.content, p.created_at, p.updated_at, u.username as author_username
       FROM posts p
       JOIN users u ON p.author_id = u.id
       WHERE p.id = $1`,
      [id]
    );
    const post = postResult.rows[0];

    if (!post) {
      return res.status(404).json({ message: 'Post not found' });
    }

    res.status(200).json(post);
  } catch (error) {
    console.error('Error getting post:', error.message);
    res.status(500).json({ message: 'Error getting post' });
  }
});

// Update a blog post (protected)
app.put('/api/posts/:id', authenticateToken, async (req, res) => {
  const { id } = req.params;
  const { title, content } = req.body;
  const author_id = req.user.id; // Ensure only the author (or admin) can update their post

  if (!title || !content) {
    return res.status(400).json({ message: 'Title and content are required' });
  }

  try {
    const result = await pool.query(
      'UPDATE posts SET title = $1, content = $2, updated_at = NOW() WHERE id = $3 AND author_id = $4 RETURNING *',
      [title, content, id, author_id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Post not found or you are not authorized to update this post' });
    }

    res.status(200).json(result.rows[0]);
  } catch (error) {
    console.error('Error updating post:', error.message);
    res.status(500).json({ message: 'Error updating post' });
  }
});

// Delete a blog post (protected)
app.delete('/api/posts/:id', authenticateToken, async (req, res) => {
  const { id } = req.params;
  const author_id = req.user.id; // Ensure only the author (or admin) can delete their post
  
  try {
    // First, delete associated comments
    await pool.query('DELETE FROM comments WHERE post_id = $1', [id]);

    // Then delete the post
    const result = await pool.query(
      'DELETE FROM posts WHERE id = $1 AND author_id = $2 RETURNING id',
      [id, author_id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Post not found or you are not authorized to delete this post' });
    }

    res.status(200).json({ message: 'Post and associated comments deleted successfully' });
  } catch (error) {
    console.error('Error deleting post:', error.message);
    res.status(500).json({ message: 'Error deleting post' });
  }
});

// --- Comments --- 

// Add a comment to a specific post (public)
app.post('/api/posts/:postId/comments', async (req, res) => {
  const { postId } = req.params;
  const { author_name, content } = req.body;

  if (!author_name || !content) {
    return res.status(400).json({ message: 'Author name and content are required for comment' });
  }

  try {
    // Check if post exists
    const postCheck = await pool.query('SELECT id FROM posts WHERE id = $1', [postId]);
    if (postCheck.rows.length === 0) {
      return res.status(404).json({ message: 'Post not found' });
    }

    const result = await pool.query(
      'INSERT INTO comments (post_id, author_name, content) VALUES ($1, $2, $3) RETURNING *',
      [postId, author_name, content]
    );
    res.status(201).json(result.rows[0]);
  } catch (error) {
    console.error('Error adding comment:', error.message);
    res.status(500).json({ message: 'Error adding comment' });
  }
});

// Get comments for a specific post (public)
app.get('/api/posts/:postId/comments', async (req, res) => {
  const { postId } = req.params;

  try {
    // Check if post exists
    const postCheck = await pool.query('SELECT id FROM posts WHERE id = $1', [postId]);
    if (postCheck.rows.length === 0) {
      return res.status(404).json({ message: 'Post not found' });
    }

    const result = await pool.query(
      'SELECT id, post_id, author_name, content, created_at FROM comments WHERE post_id = $1 ORDER BY created_at DESC',
      [postId]
    );
    res.status(200).json(result.rows);
  } catch (error) {
    console.error('Error getting comments:', error.message);
    res.status(500).json({ message: 'Error getting comments' });
  }
});

// Basic Error Handling Middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log('PostgreSQL connected via Neon DB');
});

/*

  PostgreSQL Database Schema (SQL commands):

  CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'author' NOT NULL, -- e.g., 'author', 'admin'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL, -- For rich text content
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_name VARCHAR(255) NOT NULL, -- Can be anonymous or a registered user's name
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
  );

  -- Optional: Create an admin user manually for testing if needed
  -- INSERT INTO users (username, password_hash, role) VALUES ('admin', '$2a$10$HASHED_ADMIN_PASSWORD_HERE', 'admin');
  -- Replace '$2a$10$HASHED_ADMIN_PASSWORD_HERE' with a bcrypt hash of your desired admin password.

*/