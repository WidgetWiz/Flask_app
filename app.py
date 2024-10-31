from flask import Flask, render_template, request, send_file, flash
import pandas as pd
import zipfile
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  

# Ensure the output directory exists
output_folder = 'output'
os.makedirs(output_folder, exist_ok=True)

required_columns = ['id', 'address']

# Function to validate columns
def validate_columns(df, dataset_name):
    df.columns = df.columns.str.strip().str.lower()
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"The following required columns are missing from {dataset_name}: {', '.join(missing_columns)}")
    return df

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        # Get uploaded files
        file1 = request.files['file1']
        file2 = request.files['file2']

        # Read and validate columns in the datasets
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)
        df1 = validate_columns(df1, 'Dataset 1')
        df2 = validate_columns(df2, 'Dataset 2')

        # Process datasets
        df1 = df1[required_columns].drop_duplicates()
        df2 = df2[required_columns].drop_duplicates()
        common_rows = pd.merge(df1, df2, on=required_columns)
        unique_df1 = pd.concat([df1, common_rows]).drop_duplicates(keep=False)
        unique_df2 = pd.concat([df2, common_rows]).drop_duplicates(keep=False)

        # Save results to CSV files
        common_path = os.path.join(output_folder, 'common_rows.csv')
        unique1_path = os.path.join(output_folder, 'unique_in_df1.csv')
        unique2_path = os.path.join(output_folder, 'unique_in_df2.csv')
        common_rows.to_csv(common_path, index=False)
        unique_df1.to_csv(unique1_path, index=False)
        unique_df2.to_csv(unique2_path, index=False)

        # Zip the CSV files
        zip_path = os.path.join(output_folder, 'output_datasets.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(common_path, 'common_rows.csv')
            zipf.write(unique1_path, 'unique_in_df1.csv')
            zipf.write(unique2_path, 'unique_in_df2.csv')

        flash("Processing complete! Your files are ready for download.")
        return send_file(zip_path, as_attachment=True)

    except ValueError as e:
        return render_template('error.html', message=str(e))
    except Exception as e:
        return render_template('error.html', message="An unexpected error occurred. Please try again.")

if __name__ == '__main__':
    app.run(debug=True)
