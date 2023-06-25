curl -L https://git.io/getLatestIstio | sh -
cd istio-1.18.0
sudo mv -v bin/istioctl /bin/
istioctl install -ys