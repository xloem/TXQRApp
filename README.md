# TXQRApp

Send and receive information with barcodes.  OCR is preferred to QR transmission because a human can review the data for obvious decoder exploits.  This app may not be secure, but makes life easier when interoperating with those that are.

Information flows in and out using barcodes.  The information passes through many libraries:

- the optional streaming luby transform codecs have not been tuned and reviewed for security
- zbarlight and the underlying zbar library have not been tuned and reviewed for security
- pyzint and the underlying zint library have not been tuned and reviewed for security
- kivy's camera and rendering systems and their underlying libraries have not been tuned and reviewed for security
- etc

TODO: link to other similar work .  See https://github.com/divan/txqr/issues/12 .  optionally also comment on how efforts could integrate and work be reused, for developers to enter the ecosystem effectively.

NOTE: the maximum data sizes for the different QR code sizes are enumerated at https://github.com/xloem/qrstream/blob/master/android/app/src/main/java/com/github/xloem/qrstream/QRCodeMetric.java .  The README of that project also has information on sending and receiving QR encoded files from the linux command line without any specialised tools.

It's been suggested that javascript could make for better development velocity here: https://github.com/Fiona1729/QRStreamer/issues/1#issuecomment-741759934 .  If that's true, it shouldn't be hard to port the code to javascript if anybody is interested.
