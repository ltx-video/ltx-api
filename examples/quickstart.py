        """Minimal LTX Video example: create one prediction and print the output URL(s)."""
        import ltx_api

        output = ltx_api.run({
    "image_url": "https://example.com/input.png",
    "prompt": "A cinematic shot of a lighthouse at dawn, soft fog, warm light"
})
        print(output)
