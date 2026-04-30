# Save to Second Brain — iOS Shortcut

iOS does not (yet) honour the Web Share Target manifest entry that PWAs use on
Android. The cleanest fix is a one-time iOS Shortcut that POSTs the share-sheet
input to your backend.

You can build it in 60 seconds:

1. Open the **Shortcuts** app → tap the `+` icon.
2. Add action **Receive Shortcut Input** → set type to *URLs, Text*.
3. Add action **Get Contents of URL**:
   - URL: `https://YOUR-BACKEND.onrender.com/api/share`
   - Method: `POST`
   - Request Body: `Form`
     - `text` → *Shortcut Input*
   - Headers:
     - `Authorization` → `Bearer YOUR_API_TOKEN`
4. Add action **Show Notification** with the result so you get a toast.
5. Tap settings → enable **Show in Share Sheet**.

Now in any iOS app: **Share → Save to Second Brain**.

---

## Optional: programmatic install

You can also generate a `.shortcut` file from any Mac with Shortcuts.app and
host it under `apps/web/public/save-to-second-brain.shortcut`. Users tap the
file in Safari and iOS imports it.
