import os
import csv
import json
import requests

os.makedirs("images_live", exist_ok=True)
os.makedirs("images", exist_ok=True)

def fetch_inaturalist_photo(species_name):
    url = "https://api.inaturalist.org/v1/observations"
    params = {
        "taxon_name": species_name,
        "quality_grade": "research",
        "per_page": 1,
        "photos": "true"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("results") and len(data["results"]) > 0:
                obs = data["results"][0]
                if obs.get("photos") and len(obs["photos"]) > 0:
                    photo_url = obs["photos"][0]["url"]
                    return photo_url.replace("square", "large").replace("medium", "large")
    except Exception as e:
        print("   [iNat Error] Skipping {}: {}".format(species_name, e))
    return None

def fetch_herbarium_photo(species_name):
    url = "https://api.idigbio.org/v2/search/media"
    payload = {"scientificname": species_name.lower()}
    params = {"rq": json.dumps(payload), "limit": 1}
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("items") and len(data["items"]) > 0:
                item = data["items"][0]
                index_terms = item.get("indexTerms", {})
                return index_terms.get("highresuri") or index_terms.get("accessuri")
    except Exception as e:
        print("   [Herbarium Error] Skipping {}: {}".format(species_name, e))
    return None

def download_image(url, destination_path):
    try:
        headers = {"User-Agent": "EstanciaSeedApp/1.0"}
        response = requests.get(url, headers=headers, stream=True, timeout=15)
        if response.status_code == 200:
            with open(destination_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
    except Exception as e:
        print("    Download failed: {}".format(e))
    return False

def main():
    if not os.path.exists("taxa.csv"):
        print("Error: Could not find taxa.csv in this folder!")
        return

    print("Analyzing taxa.csv for missing botanical imagery...")
    
    with open("taxa.csv", mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            species = row.get('scientificName', '').strip()
            if not species:
                continue
                
            print("\nSpecies: {}".format(species))
            
            # Check living photo
            live_path = os.path.join("images_live", "{}.jpg".format(species))
            if os.path.exists(live_path):
                print(" -> Living photo already cached.")
            else:
                print(" -> Searching iNaturalist...")
                url = fetch_inaturalist_photo(species)
                if url and download_image(url, live_path):
                    print("    Saved living photo to {}".format(live_path))
                else:
                    print("    No research-grade photo found.")

            # Check herbarium photo
            herb_path = os.path.join("images", "{}.jpg".format(species))
            if os.path.exists(herb_path):
                print(" -> Herbarium sheet already cached.")
            else:
                print(" -> Searching herbarium archives...")
                url = fetch_herbarium_photo(species)
                if url and download_image(url, herb_path):
                    print("    Saved herbarium sheet to {}".format(herb_path))
                else:
                    print("    No digitized sheet found.")

if __name__ == "__main__":
    main()