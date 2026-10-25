# Galaxy J2 Prime vendor snapshot — LineageOS 18.1

The `lineage-18.1` baseline omitted `lib/hw/camera.mt6735.so` despite retaining
the supporting camera libraries and advertising camera hardware. Restore that
42,800-byte module from this same device repository's pinned `lineage-15.1`
revision. Its Git blob hash matches the module installed on the SM-G532G used
for the 2026-10-25 audit.

See `camera-blob-provenance.json` for the source revision, Git object hash,
SHA-256, size, and direct ELF dependencies. No blob from a different device was
introduced, and no existing vendor library or device calibration was replaced.
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
