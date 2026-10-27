# Galaxy J2 Prime vendor snapshot — LineageOS 18.1

The primary audio HAL now uses this kernel's `MultiMedia2_PLayback` name for
isolated deep-buffer playback. Its previous `Deep_Buffer_PLayback` name was
absent, yielding PCM -1 and silent/frozen video playback. The same-length
20-byte string replacement leaves executable code, ordinary output paths,
microphone selectors and calibration unchanged. On-device logs confirm PCM
device 24 opens and runs. The user confirms synthetic video/tone, previously
frozen recordings, and fresh rear/front camera clips with sound and a successful
Camera reopen. Permanent installation/reboot and other audio routes remain
pending. See `audio-deep-buffer-provenance.json` and the matching device tree's
`docs/AUDIO_DEEP_BUFFER_FIX.md` / `tools/fix_audio_deep_buffer.py`.

HD recording parameter/scene getters and setters now select the correct records
in this snapshot's NVRAM table (63/64 instead of 65/66). The mismatched sizes
previously loaded DC calibration and a vibration-speaker filter as recording
parameters. Only four instruction bytes change; calibration files are untouched.
The user confirms a fresh foreground recording has a moving meter and audible
voice with the correction loaded. Recovery installation/reboot and calls still
need testing. See `recording-lid-provenance.json`, guarded
`tools/fix_recording_lids.py`, and device `docs/MICROPHONE_RECORDING_FIX.md`.

The Light driver's BACKLIGHT callback also wrote packed ARGB as signed
brightness. Android 11 supplies grayscale `0xffBBBBBB`; the kernel rejected
negative writes and left the resumed panel dark. A one-byte LDR-to-LDRB
correction decodes all 256 framework levels, leaving other callbacks unchanged.
Live brightness/three sleep-wake cycles pass; the user confirms power/home wake.
The temporary test leaves installed firmware unchanged until the ZIP is
installed. See `lights-brightness-provenance.json`, guarded
`tools/fix_lights_brightness.py`, and device `docs/BACKLIGHT_WAKE_FIX.md`.

The GPS worker now binds its stream socket at `/data/gps_mnl/codec` in the
existing GPS-owned directory. Its old `/data/misc/codec_sock` path cannot be
created by the configured GPS UID/groups on Android 11. The legacy worker's
bind-error path exits before signaling initialization ready, leaving GNSS and
system_server startup waiting indefinitely. The latest boot watchdog/native
stacks match that condition; an exact-UID socket probe reproduces EACCES in the
old parent and success in the new parent.

Only 14 bytes in one 22-byte string slot change; all executable code, ELF
headers/symbols/dependencies, process credentials and directory modes stay
identical. Calibration and normal MNL datagram paths are untouched. No other
bundled vendor file references the old socket; external factory tools may need
the new path. `gps-socket-provenance.json` records exact hashes/offset/source.
`tools/fix_gps_socket.py LIBRARY --apply` reproduces the correction, accepts a
repeat invocation and rejects unknown binaries. Pair with the matching device
tree's existing GPS-owned directory/init configuration and
`tools/validate_gnss_socket.py`. See device `docs/GNSS_BOOT_FIX.md` for the
tested single-library recovery update. The user now confirms normal boot;
satellite positioning and continued service responsiveness need testing.

The light driver has one scoped dependency correction, documented in
`lights-dependency-provenance.json`: remove its unused DT_NEEDED entry for the
missing `libsecril-client.so`. It imports no functions from that library and
has no dynamic symbol lookup. The original fails to load; the corrected driver
loads and Android 11's real HIDL wrapper enumerates a backlight. Code, symbols,
headers and file size stay unchanged. `tools/fix_lights_dependency.py` verifies
both exact hashes, applies idempotently and refuses unknown versions. Pair with
the device's Light service/wrapper and narrow backlight access rule. No radio
library or calibration is modified. After the user installed the Light update,
fresh logs passed display initialization and reached the separate GNSS gate
above; brightness range and suspend/resume testing remain pending.

The `lineage-18.1` baseline omitted `lib/hw/camera.mt6735.so` despite retaining
the supporting camera libraries and advertising camera hardware. Restore that
42,800-byte module from this same device repository's pinned `lineage-15.1`
revision. Its Git blob hash matches the module installed on the SM-G532G used
for the 2026-10-25 audit.

See `camera-blob-provenance.json` for the source revision, Git object hash,
SHA-256, size, and direct ELF dependencies. No blob from a different device was
introduced by the camera restoration, and no device calibration was replaced.
The existing recursive `PRODUCT_COPY_FILES` rule installs the restored file.

Static validation confirms an ARM ELF32 library with an `HMI` module export.
This restores a missing prerequisite; camera preview/capture is **not yet
verified**. Pair it with the device branch's camera provider service addition
and validate the legacy camera/framework ABI on Android 11. The connected ROM
reports zero cameras and lacks the provider service binary.

From the project/Android root, using the matching device tree:

```sh
python device/samsung/grandppltedx/tools/audit_vendor.py \
  vendor/samsung/grandppltedx/proprietary/vendor
```

An external ELF dependency in that report is not automatically missing: many
libraries are built by Android. Conversely, ELF inventory does not prove symbol
or namespace compatibility. Bluetooth, GNSS, audio, USB audio and DRM still
require the tests documented in the device tree's `docs/HARDWARE_BRINGUP.md`.

## Android 11 source-built library selection

The recursive blob installation excludes `lib/libalsautils.so`. Android 11's
`audio.usb.default` requires `profile_get_highest_sample_rate`, which the
bundled old library does not export. That copy previously overwrote the
source-built module, matching the linker error observed on the phone. The
MTK primary audio HAL lists this dependency but imports none of its symbols.
The original blob remains in the repository for provenance. USB playback and
capture still require device testing after building the coherent image.

The `libion_mtk` Soong module now references `libion_mtk.so`; it previously
referenced `libdpframework.so`. Only the correct blob exports
`ion_custom_ioctl`, which the device's graphics code calls. Both graphics
prebuilts are packaged through their modules, excluding duplicate raw copies.

The old `lib/libshim_gui.so` is also excluded from raw copying. It overwrote the
device's source-built shim and lacks the old unsigned mapper-lock implementation
needed by `hwcomposer.mt6735.so`. The first VM ROM consequently stayed at the
Samsung logo while Android repeatedly waited for its display service. Pair this
exclusion with the device's updated GUI shim/CallStack dependency. Before/after
`dlopen(RTLD_NOW)` tests reproduce the original composer/camera errors and load
both with the new shim; normal boot and hardware operation remain to be tested.

## Audio-filter calibration IDs

`libaudiocompensationfilter_vendor.so` used NVRAM LIDs two entries higher than
the bundled `libcustom_nvram.so` table. Its default getter/setter selected LID
53 (`WIFI`, 512 bytes) instead of 51 (`Audio_CompFlt`, 1260 bytes). The installed
phone logs the corresponding failed Wi-Fi-record access during audio-filter
initialization and falls back to default filter parameters. The filter's six
table selections have the same +2 bias.

Eight constant bytes are corrected: the getter/setter defaults and the shared
six-entry selection table. All seven filter types now resolve to the intended
audio files with 1260-byte records. No file access permissions, calibration
contents, record format, or DSP coefficients are changed. This corrects record
selection; playback quality and persistence still require physical testing.

`audio-filter-lid-provenance.json` records the original Git object, source
revision, input/output SHA-256, exact byte preconditions and offsets. Reproduce
or verify the patch with `python3 tools/fix_audio_filter_lids.py --apply` or
`python3 tools/fix_audio_filter_lids.py`. The tool rejects unknown binaries.
From the Android root, independently check both library/table contents with:

```sh
python3 device/samsung/grandppltedx/tools/validate_audio_nvram.py \
  vendor/samsung/grandppltedx/proprietary/vendor
```

The checker rejects the original library because it selects the Wi-Fi record.
The corrected library passes all seven file/type/size checks. Raw NVRAM data
was never read or modified by this source correction.
