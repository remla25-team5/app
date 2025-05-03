# app

This repository contains app-frontend and app-service components of the app-image container.


Build the image as follows

```bash
sudo docker build -t my-website .
```

It will: 
- Install frontend dependencies
- Build the frontend which produces a /dist folder inside /app-frontend
- Copy this over to /app-service
- Install all needed dependencies for backend
- Launches backend with app.py

The container will listen on port 8080, so run the container and map it to our own port 8080

```bash
sudo docker run -p 8080:8080 my-website
```

Visit http://localhost:8080 in your browser to see the website.

It might throw some errors because the backend relies on some other backend which might not be up and running!
