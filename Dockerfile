# Step 1: Use an official Python image as the base image
FROM python:3.10-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the requirements.txt (or copy your entire app)
COPY requirements.txt /app/

# Step 4: Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of the application
COPY . /app/

# Step 6: Expose the port that FastAPI will run on
EXPOSE 8000

# Step 7: Run the app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]