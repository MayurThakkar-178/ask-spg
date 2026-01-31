import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract
import re
import os

# Set page config
st.set_page_config(page_title="Marketing Email Extractor", layout="centered")

def extract_emails(text):
    """Extracts unique email addresses from text using regex."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return list(set(emails))  # Return unique emails

def main():
    st.title("📧 Marketing Email CSV Creator")
    st.markdown("Extract emails from **Images** and **Text** and save them for your marketing campaigns.")

    # Input Section
    st.header("1. Input Data")
    
    # Image Upload
    uploaded_files = st.file_uploader("Upload Images (containing emails)", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
    
    # Text Input
    raw_text = st.text_area("Paste Text (containing emails)", height=150, placeholder="Paste email lists, raw text, or messages here...")

    # Action Section
    if st.button("Extract & Save CSV", type="primary"):
        all_text = raw_text + "\n"
        
        # Process Images
        if uploaded_files:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_files = len(uploaded_files)
            
            for i, uploaded_file in enumerate(uploaded_files):
                try:
                    status_text.text(f"Processing image {i+1} of {total_files}...")
                    image = Image.open(uploaded_file)
                    
                    # Optimization 1: Convert to Grayscale
                    image = image.convert('L')
                    
                    # Optimization 2: Resize if too large (e.g., width > 1800)
                    # This significantly speeds up OCR without losing much accuracy for text
                    max_width = 1800
                    if image.width > max_width:
                        ratio = max_width / image.width
                        new_height = int(image.height * ratio)
                        image = image.resize((max_width, new_height))
                        
                    # Perform OCR
                    text = pytesseract.image_to_string(image)
                    all_text += text + "\n"
                    
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {e}")
                
                # Update progress
                progress_bar.progress((i + 1) / total_files)
            
            status_text.text("Processing complete!")
            progress_bar.empty()

        # Extract Emails
        emails = extract_emails(all_text)

        if emails:
            st.success(f"Found {len(emails)} unique emails!")
            
            # Create DataFrame
            df = pd.DataFrame(emails, columns=["Email"])
            
            # Show Preview
            st.dataframe(df, use_container_width=True)

            # Save to specific directory
            target_dir = os.path.expanduser("~/Documents/ShahPatel")
            target_file = os.path.join(target_dir, "marketing_emails.csv")

            try:
                # Ensure directory exists
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                    st.info(f"Created directory: {target_dir}")

                # Save file
                df.to_csv(target_file, index=False)
                st.toast(f"Saved to: {target_file}", icon="✅")
                st.markdown(f"### ✅ File Saved Successfully!\nLocation: `{target_file}`")
                
                # Also provide a download button as backup
                st.download_button(
                    label="Download CSV backup",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name='marketing_emails_backup.csv',
                    mime='text/csv',
                )

            except PermissionError:
                st.error(f"❌ Permission Denied: Cannot write to `{target_dir}`. Please check folder permissions.")
            except Exception as e:
                st.error(f"❌ Error saving file: {e}")

        else:
            st.warning("No email addresses found in the provided images or text.")

if __name__ == "__main__":
    main()
