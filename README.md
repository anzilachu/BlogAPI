# API Endpoints Documentation

This document provides instructions on how to test each endpoint of the API.


## Endpoints

### Authors

1. List Authors
   - GET `/authors/`
   - No authentication required

2. Create Author
   - POST `/authors/`
   - Body: `{"name": "John Doe", "email": "anzil@example.com", "password": "securepassword", "bio": "Optional bio"}`
   - No authentication required

3. Retrieve Author
   - GET `/authors/{author_id}/`
   - No authentication required

4. Update Author
   - PUT/PATCH `/authors/{author_id}/`
   - Requires authentication
   - Can only be done by the author or staff

5. Delete Author
   - DELETE `/authors/{author_id}/`
   - Requires authentication
   - Can only be done by the author or staff

### Posts

1. List Posts
   - GET `/posts/`
   - No authentication required

2. Create Post
   - POST `/posts/`
   - Requires authentication
   - Body: `{"title": "Post Title", "content": "Post content", "location": "Optional location"}`

3. Retrieve Post
   - GET `/posts/{post_id}/`
   - No authentication required

4. Update Post
   - PUT/PATCH `/posts/{post_id}/`
   - Requires authentication
   - Can only be done by the author

5. Delete Post
   - DELETE `/posts/{post_id}/`
   - Requires authentication
   - Can only be done by the author

### Authentication

1. Login
   - POST `/login/`
   - Body: `{"email": "user@example.com", "password": "userpassword"}`
   - Returns access and refresh tokens

2. Logout
   - POST `/logout/`
   - Body: `{"refresh": "your_refresh_token_here"}`
   - Blacklists the refresh token
