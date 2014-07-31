# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"

  config.omnibus.chef_version = :latest

  config.vm.network :forwarded_port, guest: 3306, host: 3306
  config.vm.network :private_network, ip: "192.168.33.10"

  config.vm.synced_folder ".", "/home/vagrant/app"

  config.vm.provider :virtualbox do |vb|
    # Don't boot with headless mode
    vb.gui = false

    # Use VBoxManage to customize the VM. For example to change memory:
    vb.customize ["modifyvm", :id, "--memory", "1024"]
  end

  config.vm.provider :lxc do |lxc, override|
    override.vm.box = "fgrehm/trusty64-lxc"
  end

  config.vm.provision :chef_solo do |chef|
    chef.cookbooks_path = "vagrant/cookbooks"
    chef.roles_path     = "vagrant/roles"
    chef.data_bags_path = "vagrant/data_bags"
    chef.add_role "sharpefolio-vagrant"
  end
end
