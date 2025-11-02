# The-Smart-AI
1. Introduction
1.1 Purpose

The purpose of this project is to develop a smart, searchable directory of AI tools. Users can browse, search, and filter AI tools based on task, category, pricing, and rating. The platform aims to help students, developers, content creators, and researchers discover the most relevant AI tools for their needs.

1.2 Scope

User authentication (login/register)

Google OAuth integration

Smart tool search and filtering

Category-based browsing

Tool ratings, tags, and detailed descriptions

Admin panel for tool management

Favorite and review functionality (optional/for future enhancement)

2. Overall Description
2.1 Product Perspective

This is a web-based application developed using Python’s Flask framework. It uses SQLite as the backend database and Bootstrap for responsive UI.

2.2 User Classes and Characteristics

Guest: Can browse and search tools without login.

User: Can log in, manage account, access search and categories.

Admin: Can manage tool listings and perform moderation.

2.3 Operating Environment

Python 3.9 – 3.11

Flask framework

SQLite (local DB)

HTML5/CSS3 + Bootstrap

Browser: Chrome, Firefox, Edge

2.4 Design/Implementation Constraints

JSON file (tools.json) for storing AI tool metadata

SQLite for user data and reviews

Hosted locally or on platforms like Render/Heroku

3. Functional Requirements
3.1 User Authentication

Register with username and password

Secure login using bcrypt hashing

Optional: Login via Google OAuth

3.2 Smart Search

Search AI tools using prompt-based keywords

Filter tools by pricing (Free, Paid)

Filter tools by category or tag

Sort tools by rating or name

3.3 Tool Display

Show cards for each tool with:

Name, category, description

Pricing, rating, tags

Redirect link (Visit Tool)

3.4 Admin Panel

Add new tools

Delete or manage tool entries

View tool listings

4. Non-Functional Requirements
4.1 Usability

Clean and professional UI using Bootstrap

Fully responsive on mobile and desktop

4.2 Performance

Load time < 2 seconds for home page

Efficient filtering from JSON (~100+ tools)

4.3 Security

Passwords stored using bcrypt

Session-based authentication

SQL injection and XSS mitigated

4.4 Maintainability

Easy to scale by adding tools in tools.json

Modular Python code in app.py, recommender.py, and templates

5. Technologies Used
Component	Technology
Backend	Python (Flask)
Frontend	HTML, CSS, Bootstrap
Database	SQLite
Authentication	Flask-Bcrypt, Flask-Dance (Google)
Storage	JSON (tools.json)
Version Control	Git
6. Future Enhancements

Tool rating and review system

Favorites and bookmarking

User analytics dashboard

Tool suggestion AI model

Deployment to cloud (Heroku, Render, AWS)
