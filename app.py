
from flask import Flask, render_template, request, send_file, flash
import pandas as pd
import zipfile
import os
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Ensure the output directory exists
output_folder = 'output'
os.makedirs(output_folder, exist_ok=True)

# Function to validate columns - no specific required columns now
def validate_columns(df, dataset_name):
    df.columns = df.columns.str.strip().str.lower()
    return df

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        # Get uploaded files
        file1 = request.files.get('file1')
        file2 = request.files.get('file2')
        
        if not file1 or not file2:
            flash("Please upload both CSV files to proceed.")
            return render_template('upload.html')

        # Read and validate columns in the datasets
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
        df1 = validate_columns(df1, 'Dataset 1')
        df2 = validate_columns(df2, 'Dataset 2')

        # Process datasets - retain all columns and drop duplicates based on all columns
        common_rows = pd.merge(df1, df2, how='inner')
        unique_df1 = pd.concat([df1, common_rows]).drop_duplicates(keep=False)
        unique_df2 = pd.concat([df2, common_rows]).drop_duplicates(keep=False)

        # Create a zip file in memory
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("common_rows.csv", common_rows.to_csv(index=False))
            zipf.writestr("unique_in_df1.csv", unique_df1.to_csv(index=False))
            zipf.writestr("unique_in_df2.csv", unique_df2.to_csv(index=False))
        
        zip_buffer.seek(0)  # Reset buffer position to the beginning

        flash("Processing complete! Your files are ready for download.")
        return send_file(zip_buffer, as_attachment=True, download_name="output_datasets.zip")

    except ValueError as e:
        return render_template('error.html', message=str(e))
    except Exception as e:
        return render_template('error.html', message="An unexpected error occurred. Please try again.")

if __name__ == '__main__':
    app.run(debug=True)
