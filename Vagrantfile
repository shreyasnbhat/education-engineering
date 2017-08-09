$script = <<SCRIPT
sudo apt-get update
sudo apt-get install -y git
sudo apt-get install -y python-pip
pip install flask
SCRIPT

Vagrant.configure('2') do |config|
	config.vm.box = "ubuntu/trusty64"
	config.vm.box_url = "http://files.vagrantup.com/precise64.box"
	config.vm.provision "shell", inline: $script
 	config.vm.network "forwarded_port", guest: 8000, host: 8000, host_ip: "127.0.0.1"
 	config.vm.network "forwarded_port", guest: 8080, host: 8080, host_ip: "127.0.0.1"
 	config.vm.network "forwarded_port", guest: 5000, host: 5000, host_ip: "127.0.0.1"
	config.vm.synced_folder "flask-app/", "/home/vagrant/flask-app"
	config.vm.provider "virtualbox" do |v|
		v.memory = 4096
		v.cpus = 4
	end
end

	
	
