"""The same client drives every hosted model listed in ltx_api.MODELS."""
from ltx_api import Client, MODELS

client = Client()
for slug, info in MODELS.items():
    print(slug, "->", info["category"], "required:", info["required"])
# pick one explicitly
output = client.run({"audio_url": "https://example.com/input.png"}, model="lightricks/ltx-2.5-audio-to-video")
print(output)
