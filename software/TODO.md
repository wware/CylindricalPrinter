Stuff left to do
==

* Add an input for scale. Slider and text window, they update each other. Reset button to go back to 1.0.
* Add a checkbox for inches versus millimeters versus centimeters. Separate multiplier on top of the scale input.
* File chooser and uploader for STLs: http://stackoverflow.com/questions/10997263/html-file-picker-with-jquery

Stuff for the RPi
--

First do this on the RPi

```bash
sudo apt-get update
sudo apt-get install -y git
git clone https://github.com/wware/CylindricalPrinter.git
cd CylindricalPrinter/software
```

Then you can get to this file, where you can just copy and paste the rest.

```bash
sudo apt-get install -y vim python-dev python-virtualenv imagemagick build-essential

sudo cat > /etc/networking/interfaces <<EOF
auto lo
iface lo inet loopback
iface eth0 inet dhcp
allow-hotplug wlan0
iface wlan0 inet manual
wpa-roam /etc/wpa_supplicant/wpa_supplicant.conf
iface default inet dhcp
EOF

sudo cat > /etc/wpa_supplicant/wpa_supplicant.conf <<EOF
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
network={
    ssid="Linksys10206"
    proto=RSN
    key_mgmt=WPA-PSK
    pairwise=CCMP TKIP
    group=CCMP TKIP
    psk="PASSWORD"
}
EOF
```

Replace "PASSWORD" withn the actual WPA password. Then type

```bash
sudo ifdown wlan0; sudo ifup wlan0
```