# Keep Android 11's libalsautils paired with its audio.usb.default HAL. The
# bundled older copy lacks profile_get_highest_sample_rate and overwrites the
# source-built library. The MTK primary HAL has no symbol imports from it.
# The two graphics prebuilts are installed through their Soong modules so a
# recursive copy cannot also claim their output paths.
# Keep the source-built GUI shim: the old blob lacks Android 11 mapper-lock
# compatibility and prevents the hardware composer/SurfaceFlinger from loading.
PRODUCT_PACKAGES += libdpframework libion_mtk

PRODUCT_COPY_FILES += $(filter-out \
    vendor/samsung/grandppltedx/proprietary/vendor/lib/libalsautils.so:% \
    vendor/samsung/grandppltedx/proprietary/vendor/lib/libdpframework.so:% \
    vendor/samsung/grandppltedx/proprietary/vendor/lib/libion_mtk.so:% \
    vendor/samsung/grandppltedx/proprietary/vendor/lib/libshim_gui.so:%,\
    $(call find-copy-subdir-files,*,vendor/samsung/grandppltedx/proprietary/vendor,$(TARGET_COPY_OUT_VENDOR)))


