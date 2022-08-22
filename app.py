# Core package
import streamlit as st
import streamlit.components.v1 as stc

# External dependencies
from utils import *
from db_utils import *

# General packages
import pandas as pd
from datetime import datetime
import os
import time

# Image packages
from PIL import Image
import exifread
import base64

# Audio package
import mutagen

# PDF package
from PyPDF2 import PdfFileReader

# Data Visualization packages
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")

# HTML
metadata_wiki = """
Metadata is defined as the data providing information about one or more aspects of the data. 
It is used to summarize basic information about data which can make tracking and working with specific data easier
"""

HTML_BANNER = """
    <div style="background-color:#464e5f;padding:10px;border-radius:10px">
    <h1 style="color:white;text-align:center;">Metadata Extractor App</h1>
    </div>
"""

timestr = time.strftime("%Y%m%d-%H%M%S")


# Functions
@st.cache
def load_image(image_file):
    img = Image.open(image_file)
    return img


def make_downloadable(data):
    csvfile = data.to_csv(index=False)
    # B64 encoding
    b64 = base64.b64encode(csvfile.encode()).decode()
    st.markdown("### ** Download CSV File")
    new_filename = "metadata_result_{}_.csv".format(timestr)
    href = f'<a href="data:file/csv;base64,{b64}" download = {new_filename}>Click Here To Download</a>'
    st.markdown(href, unsafe_allow_html=True)


# App Structure
def main():
    """Meta Data Extraction App"""
    # st.title("MetaData Extraction App")
    stc.html(HTML_BANNER)

    menu = ["Home", "Image", "Audio", "DocumentFiles", "Analytics", "About"]
    choice = st.sidebar.selectbox("Menu", menu)
    create_uploaded_filestable()

    if choice == "Home":
        # Image
        st.image(load_image("images/metadataextraction_app_jcharistech.png"))
        # Description
        st.write(metadata_wiki)
        # Expanders & Columns
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.expander("Get Image Metadata 📷"):
                st.info("Image Metadata")
                st.markdown("📷")
                st.text("Upload JPEG, JPG, PNG Images")
        with col2:
            with st.expander("Get Audio Metadata 🔉"):
                st.info("Audio Metadata")
                st.markdown("🔉")
                st.text("Upload MP3, Ogg Audio files")
        with col3:
            with st.expander("Get Document Metadata 📄"):
                st.info("Document Metadata")
                st.markdown("📄")
                st.text("Upload PDF, DOCx Documents")

    elif choice == "Image":
        st.subheader("Image MetaData Extraction")
        image_file = st.file_uploader("Upload Image", type=["png", "jpeg", "jpg"])
        if image_file is not None:
            # UploadFile Class is File-Like Binary Byte
            # st.write(type(image_file))
            # st.write(dir(image_file))
            with st.expander("File Stats"):
                statinfo = os.stat(image_file.readable())
                file_details_combined = {
                    "FileName": image_file.name,
                    "FileSize": image_file.size,
                    "FileType": image_file.type,
                    "Accessed_Time": get_readable_time(statinfo.st_atime),
                    "Creation Time": get_readable_time(statinfo.st_ctime),
                    "Modified_Time": get_readable_time(statinfo.st_mtime),
                }
                # convert to DataFrame
                df_file_details = pd.DataFrame(
                    list(file_details_combined.items()), columns=["Meta Tags", "Value"]
                )
                st.table(df_file_details)

                # Track details
                add_file_details(
                    image_file.name, image_file.type, image_file.size, datetime.now()
                )

            # Layout
            icol1, icol2 = st.columns(2)
            with icol1:
                with st.expander("View Image"):
                    img = load_image(image_file)
                    st.image(img, width=250)

            with icol2:
                with st.expander("Default(JPEG)"):
                    st.info("Using PILLOW")
                    img = load_image(image_file)
                    # st.write(dir(img))
                    img_details = {
                        "format": img.format,
                        "format_desc": img.format_description,
                        "filename": img.filename,
                        "height": img.height,
                        "width": img.width,
                        "info": img.info,
                        # "encoder": img.encoderinfo,
                    }
                    # convert to DataFrame
                    df_img_details = pd.DataFrame(
                        list(img_details.items()), columns=["Meta Tags", "Value"]
                    )
                    st.dataframe(df_img_details)

            # Layout for Forensics
            fcol1, fcol2 = st.columns(2)
            with fcol1:
                with st.expander("Exifread Tool"):
                    meta_tags = exifread.process_file(image_file)
                    # convert to DataFrame
                    if len(meta_tags) > 0:
                        tag_names, values = zip(*meta_tags.items())
                        values_str = [str(a) for a in values]
                        df_img_details_exifread = pd.DataFrame(
                            {"Meta Tags": tag_names, "Value": values_str}
                        )
                        st.dataframe(df_img_details_exifread)

                    else:
                        st.info("NO EXIF DATA")

            with fcol2:
                with st.expander("Image Geo-Coordinates"):
                    img_details_with_exif = get_exif(image_file)
                    img_coordinates = get_decimal_coordinates(img_details_with_exif)
                    if img_coordinates is not None:
                        st.write(img_coordinates)
                    else:
                        st.info("NO GEO TAG")

            with st.expander("Donwload Results"):

                final_df = pd.concat(
                    [df_file_details, df_img_details, df_img_details_exifread]
                )
                st.dataframe(final_df)
                make_downloadable(final_df)

    elif choice == "Audio":
        st.subheader("Audio MetaData Extraction")

        # File Upload
        audio_file = st.file_uploader("Upload Audio", type=["mp3", "ogg"])
        if audio_file is not None:
            with st.expander("Play Audio File"):
                st.audio(audio_file.read())

            # Layout
            acol1, acol2 = st.columns(2)
            with acol1:
                with st.expander("File Stats"):
                    statinfo = os.stat(audio_file.readable())
                    file_details_combined = {
                        "FileName": audio_file.name,
                        "FileSize": audio_file.size,
                        "FileType": audio_file.type,
                        "Accessed_Time": get_readable_time(statinfo.st_atime),
                        "Creation Time": get_readable_time(statinfo.st_ctime),
                        "Modified_Time": get_readable_time(statinfo.st_mtime),
                    }
                    # convert to DataFrame
                    df_file_details = pd.DataFrame(
                        list(file_details_combined.items()),
                        columns=["Meta Tags", "Value"],
                    )
                    st.table(df_file_details)

                    # Track details
                    add_file_details(
                        audio_file.name,
                        audio_file.type,
                        audio_file.size,
                        datetime.now(),
                    )

            with acol2:
                with st.expander("Metadata with Mutagen"):
                    # st.write(dir(mutagen))
                    meta_tags = mutagen.File(audio_file)
                    tag_names, values = zip(*meta_tags.items())
                    values_str = [str(a) for a in values]
                    df_audio_details_mutagen = pd.DataFrame(
                        {"Meta Tags": tag_names, "Value": values_str}
                    )
                    st.table(df_audio_details_mutagen)

            with st.expander("Donwload Results"):
                final_df = pd.concat([df_file_details, df_audio_details_mutagen])
                st.table(final_df)
                make_downloadable(final_df)

    elif choice == "DocumentFiles":
        st.subheader("DocumentFiles MetaData Extraction")
        text_file = st.file_uploader("Upload Image", type=["pdf"])

        if text_file is not None:

            dcol1, dcol2 = st.columns(2)

            with dcol1:

                with st.expander("File Stats"):
                    statinfo = os.stat(text_file.readable())
                    file_details_combined = {
                        "FileName": text_file.name,
                        "FileSize": text_file.size,
                        "FileType": text_file.type,
                        "Accessed_Time": get_readable_time(statinfo.st_atime),
                        "Creation Time": get_readable_time(statinfo.st_ctime),
                        "Modified_Time": get_readable_time(statinfo.st_mtime),
                    }
                    # convert to DataFrame
                    df_file_details = pd.DataFrame(
                        list(file_details_combined.items()),
                        columns=["Meta Tags", "Value"],
                    )
                    st.table(df_file_details)

                    # Track details
                    add_file_details(
                        text_file.name, text_file.type, text_file.size, datetime.now()
                    )

            with dcol2:

                with st.expander("Metadata"):
                    pdf_file = PdfFileReader(text_file)
                    pdf_info = pdf_file.getDocumentInfo()
                    df_pdf_details = pd.DataFrame(
                        list(pdf_info.items()), columns=["Meta Tags", "Value"]
                    )
                    df_pdf_details["Meta Tags"] = df_pdf_details[
                        "Meta Tags"
                    ].str.replace("/", "")
                    st.dataframe(df_pdf_details)

            with st.expander("Donwload Results"):
                final_df = pd.concat([df_file_details, df_pdf_details])
                st.table(final_df)
                make_downloadable(final_df)

    elif choice == "Analytics":
        st.subheader("Analytics")
        all_uploaded_files = view_all_data()
        df = pd.DataFrame(
            all_uploaded_files,
            columns=["FileName", "FileType", "FileSize", "UploadDate"],
        )

        # Monitor all uploads
        with st.expander("Monitor"):
            st.success("View all Uploaded Files")
            st.dataframe(df)

        # Stats of Uploaded Files
        with st.expander("Distribution of FileTypes"):
            fig = plt.figure()
            sns.countplot(df["FileType"])
            st.pyplot(fig)

    else:
        st.subheader("About")


if __name__ == "__main__":
    main()
