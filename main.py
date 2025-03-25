from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import uuid
import os
import json

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
BLOGS_FILE = 'blogs.json'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load blogs from file
def load_blogs():
    if os.path.exists(BLOGS_FILE):
        with open(BLOGS_FILE, 'r') as file:
            return json.load(file)
    return []
# Save blogs to file
def save_blogs(blogs):
    with open(BLOGS_FILE, 'w') as file:
        json.dump(blogs, file, indent=4)

# Initialize blogs list
blogs = load_blogs()
@app.route('/generate-blog', methods=['POST'])
def generate_blog():
    title = request.form.get('title')
    content = request.form.get('content')
    tags = request.form.get('tags')
    if not title or not content:
        return jsonify({"message": "Title and content are required"}), 400

    cover_image = request.files.get('coverImage')
    image_url = None

    if cover_image and cover_image.filename != '':
        image_filename = f"{uuid.uuid4()}_{cover_image.filename}"
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        cover_image.save(image_path)
        image_url = f"http://127.0.0.1:5000/uploads/{image_filename}"

    new_blog = {
        "id": str(uuid.uuid4()),
        "title": title,
        "tags": tags,
        "content": content,
        "image_url": image_url,
    }

    blogs.append(new_blog)
    save_blogs(blogs)  # Save to file

    return jsonify(new_blog), 201

@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Route to fetch all blog posts (renamed to `/posts`)
@app.route('/blogs', methods=['GET'])
def get_posts():
    search = request.args.get('search', '')
    filtered_blogs = [blog for blog in blogs if search.lower() in blog['title'].lower()]
    return jsonify(filtered_blogs), 200

@app.route('/blogs/<blog_id>', methods=['GET'])
def get_blog(blog_id):
    for blog in blogs:
        if blog["id"] == blog_id:
            return jsonify(blog), 200
    return jsonify({"message": "Blog not found"}), 404

@app.route('/blogs/<blog_id>', methods=['DELETE'])
def delete_blog(blog_id):
    global blogs
    blogs = [blog for blog in blogs if blog["id"] != blog_id]
    save_blogs(blogs)  # Save updated list to file
    return jsonify({"message": "Blog deleted"}), 200

@app.route('/blogs/<blog_id>', methods=['PUT'])
def edit_blog(blog_id):
    data = request.json
    for blog in blogs:
        if blog["id"] == blog_id:
            blog["title"] = data.get("title", blog["title"])
            blog["content"] = data.get("content", blog["content"])
            blog["tags"] = data.get("tags", blog["tags"])
            save_blogs(blogs)
            return jsonify({"message": "Blog updated successfully", "blog": blog}), 200
    return jsonify({"message": "Blog not found"}), 404

@app.route('/blogs/<blog_id>/comments', methods=['POST'])
def add_comment(blog_id):
    data = request.json
    for blog in blogs:
        if blog["id"] == blog_id:
            blog["comments"].append(data)
            save_blogs(blogs)
            return jsonify({"message": "Comment added successfully", "blog": blog}), 200
    return jsonify({"message": "Blog not found"}), 404

if __name__ == '__main__':
    app.run()
