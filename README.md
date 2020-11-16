# TXQRApp

Send and receive information with barcodes.  This app may not be secure.

Information flows in and out using barcodes.  The information passes through many libraries:

- the optional streaming luby transform codecs have not been tuned and reviewed for security
- zbarlight and the underlying zbar library have not been tuned and reviewed for security
- pyzint and the underlying zint library have not been tuned and reviewed for security
- kivy's camera and rendering systems and their underlying libraries have not been tuned and reviewed for security

TODO: link to other similar work
