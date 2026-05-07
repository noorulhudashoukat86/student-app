CREATE DATABASE IF NOT EXISTS studentdb;
USE studentdb;

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    roll_no VARCHAR(50) UNIQUE NOT NULL,
    department VARCHAR(100),
    gpa DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO students (name, email, roll_no, department, gpa) VALUES
('Ali Hassan', 'ali@university.edu', 'BCS-001', 'Computer Science', 3.8),
('Sara Khan', 'sara@university.edu', 'BDS-001', 'Data Science', 3.6),
('Usman Raza', 'usman@university.edu', 'BAI-001', 'Artificial Intelligence', 3.9);
