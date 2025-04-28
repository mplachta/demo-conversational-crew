import os
import glob

# Find all mdx files in the knowledge/oss-docs directory
mdx_files = glob.glob("oss-docs/**/*.mdx", recursive=True)

# Process each MDX file
for file_path in mdx_files:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            url = "Documentation page URL: " + file_path.replace("oss-docs/", "https://docs.crewai.com/").replace(".mdx", "")

            with open(file_path, 'w', encoding='utf-8') as outfile:
                outfile.write(f"{url}\n\n{content}")
        
        print(f"Processed {file_path}")
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
