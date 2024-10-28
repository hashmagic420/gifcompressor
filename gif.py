import streamlit as st
from PIL import Image, ImageSequence
import io

def compress_gif(image_bytes, resize_width=None, resize_height=None, optimize=True, loop=0, duration=100):
    # Open the original GIF
    original_gif = Image.open(io.BytesIO(image_bytes))

    # Prepare a list to hold the frames
    frames = []

    # Calculate aspect ratio if necessary
    if resize_width and not resize_height:
        aspect_ratio = original_gif.height / original_gif.width
        resize_height = int(resize_width * aspect_ratio)
    elif resize_height and not resize_width:
        aspect_ratio = original_gif.width / original_gif.height
        resize_width = int(resize_height * aspect_ratio)

    # Iterate over each frame in the original GIF
    for frame in ImageSequence.Iterator(original_gif):
        # Resize the frame if dimensions are provided
        if resize_width or resize_height:
            resize_dimensions = (
                resize_width if resize_width else frame.width,
                resize_height if resize_height else frame.height
            )
            frame = frame.resize(resize_dimensions, Image.LANCZOS)

        # Convert to palette mode to reduce file size
        frame = frame.convert('P', palette=Image.ADAPTIVE)

        frames.append(frame)

    # Save the frames as a new GIF
    output_bytes_io = io.BytesIO()
    frames[0].save(
        output_bytes_io,
        format='GIF',
        save_all=True,
        append_images=frames[1:],
        optimize=optimize,
        loop=loop,
        duration=duration
    )

    output_bytes_io.seek(0)
    return output_bytes_io

# Streamlit App
st.title("GIF Compressor and Resizer")

st.write("Upload a GIF image, adjust compression settings, and download the compressed GIF.")

# File uploader
uploaded_file = st.file_uploader("Choose a GIF file", type="gif")

if uploaded_file is not None:
    try:
        # Display original GIF
        st.subheader("Original GIF")
        st.image(uploaded_file, use_column_width=True)

        # Compression settings
        st.subheader("Compression Settings")

        resize_width = st.number_input("Resize Width (px)", min_value=0, value=0)
        resize_height = st.number_input("Resize Height (px)", min_value=0, value=0)

        duration = st.number_input("Frame Duration (ms)", min_value=1, value=100)
        optimize = st.checkbox("Optimize GIF", value=True)
        loop = st.number_input("Number of Loops (0 for infinite)", min_value=0, value=0)

        # Compress button
        if st.button("Compress and Resize GIF"):
            with st.spinner("Processing..."):
                # Handle zero values for dimensions
                width = int(resize_width) if resize_width else None
                height = int(resize_height) if resize_height else None

                output_gif_bytes_io = compress_gif(
                    uploaded_file.getvalue(),
                    resize_width=width,
                    resize_height=height,
                    optimize=optimize,
                    loop=loop,
                    duration=duration
                )

            # Display compressed GIF
            st.subheader("Compressed GIF")
            st.image(output_gif_bytes_io, use_column_width=True)

            # Download button
            st.download_button(
                label="Download Compressed GIF",
                data=output_gif_bytes_io,
                file_name="compressed.gif",
                mime="image/gif"
            )
    except Exception as e:
        st.error(f"An error occurred: {e}")
