import binascii
import tkinter as tk
import psycopg2
from tkinter import PhotoImage
from PIL import Image, ImageTk
from io import BytesIO
from dotenv import load_dotenv
import os

load_dotenv()


def resize_and_save_image(input_path, output_path, new_width, new_height):
    # Open the input image
    image = Image.open(input_path)

    # Calculate the aspect ratio
    aspect_ratio = float(new_width) / float(image.size[0])
    new_height = int(float(image.size[1]) * float(aspect_ratio))

    # Resize the image using the resize method with ANTIALIAS filter
    resized_image = image.resize((new_width, new_height))

    # Save the resized image
    resized_image.save(output_path)


# Function to save an image to the database
def save_image_to_db(image_path):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            host=os.getenv('HOST'),
            database=os.getenv('DATABASE'),
            user=os.getenv('USER'),
            password=os.getenv('PASSWORD')
        )

        # Create a cursor object
        cur = conn.cursor()

        # Read the image file
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        # Insert the image into the database
        cur.execute("INSERT INTO images (image_data) VALUES (%s) RETURNING id;", (image_data,))
        image_id = cur.fetchone()[0]

        # Commit the transaction
        conn.commit()

        # Close the cursor and the connection
        cur.close()
        conn.close()

        return image_id
    except Exception as e:
        print("Error:", e)


# Function to retrieve and display an image from the database
def display_image_from_db(image_id):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            host=os.getenv('HOST'),
            database=os.getenv('DATABASE'),
            user=os.getenv('USER'),
            password=os.getenv('PASSWORD')
        )

        # Create a cursor object
        cur = conn.cursor()

        # Fetch the image data from the database
        cur.execute("SELECT image_data FROM images WHERE id = %s;", (image_id,))
        image_data = cur.fetchone()[0]

        # image_data = zlib.decompress(image_data)

        hexadecimal_data = binascii.hexlify(image_data).decode('utf-8')
        print(hexadecimal_data)
        print(len(hexadecimal_data))

        # Create a Tkinter window to display the image
        image_window = tk.Toplevel()
        image_window.title("Image Viewer")

        # Create a PhotoImage object from the image data
        img = Image.open(BytesIO(image_data))
        print(img)
        img = ImageTk.PhotoImage(img)

        # Create a label to display the image
        label = tk.Label(image_window, image=img)
        label.image = img
        label.pack()

        # Close the cursor and the connection
        cur.close()
        conn.close()
    except Exception as e:
        print("Error:", e)


# Example usage:
# Save an image to the database and retrieve/display it
resize_and_save_image("image.jpg", "resized_image.jpg", new_width=300, new_height=300)

image_id = save_image_to_db("resized_image.jpg")
display_image_from_db(image_id)

# Start the Tkinter main loop
tk.mainloop()
