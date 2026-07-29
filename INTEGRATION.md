# Integrating CameraCapture into ai_daktari.html and add_product.html

## 1. Files to add
Copy into the project:
- `static/js/camera-capture.js`
- `static/css/camera-capture.css` (or paste into your existing stylesheet)

## 2. Remove the old capture attribute
Find the current "Piga Picha" markup — something like:

```html
<input type="file" accept="image/*" capture="environment" id="camera-input-hidden" class="hidden">
<button type="button" onclick="document.getElementById('camera-input-hidden').click()">
  Piga Picha
</button>
```

Replace it with a plain button (no hidden capture input needed anymore):

```html
<button type="button" id="btn-piga-picha">
  Piga Picha
</button>
```

## 3. Keep the gallery input exactly as-is
Your existing "Chagua kutoka Picha" gallery `<input type="file">` and its
`change` handler (preview rendering, etc.) do NOT need to change — that flow
already works fine and isn't affected by this bug.

```html
<input type="file" accept="image/*" id="product-image-input">
```

(Use whatever id this input already has in each template — pass that same id
as `fileInputId` below.)

## 4. Wire it up
At the bottom of the page, after the CSS/JS are loaded:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/camera-capture.css') }}">
<script src="{{ url_for('static', filename='js/camera-capture.js') }}"></script>
<script>
  new CameraCapture({
    triggerBtnId: 'btn-piga-picha',
    fileInputId: 'product-image-input'   // <- the existing gallery input's id
  });
</script>
```

That's it — do this once in `add_product.html` (pointing at its own gallery
input id) and once in `ai_daktari.html` (pointing at its own gallery input
id). Both pages share the same `camera-capture.js`/`.css` files.

## Behavior notes
- Tapping "Piga Picha" opens a full-screen in-page live preview (no native
  camera app, no backgrounded tab — this is what fixes the Android low-RAM
  bug).
- Capture button snapshots the video frame to a JPEG (0.85 quality) and
  injects it into the existing gallery `<input>` via `DataTransfer`, then
  fires a real `change` event — so your existing preview/upload logic runs
  unmodified, exactly as if the user had picked it from the gallery.
- If `getUserMedia` fails or isn't supported (old browser, permission
  denied, camera in use elsewhere), an inline error tells the user to fall
  back to "Chagua kutoka Picha" — gallery picking is untouched and always
  works.
- A camera-switch button toggles front/rear (`facingMode`) in case the rear
  camera isn't available or the user wants a selfie-style shot for a
  different use case later.
- Streams are always stopped (`getTracks().forEach(t => t.stop())`) on close
  or successful capture, so the camera light/battery drain doesn't linger.

## Suggested test pass
Same device you found the bug on (Android 10, low-RAM) — confirm:
1. Live preview opens and stays visible (tab is never backgrounded).
2. Capture produces a file that shows correctly in the existing preview UI.
3. Submitting the form uploads the captured photo successfully.
4. Denying camera permission shows the fallback error instead of crashing.
