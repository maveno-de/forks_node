# maveno-forks

Ansible Role for Chia Fork Node Deployment and Management

Version 0.1.0

Copyright (C) 2021 Javanaut

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

## NOTE

This stuff is completely experimental currently. Better read before trying out :)

## Requirements and prerequisites

This role is designed to manage nodes running Debian type OS, e.g. Debian, Ubuntu, Raspberry Pi OS.

Hardware suitable to run nodes are servers along with common PC or laptops as well as ARM based smallscale systems like RPi4 (>= 4GB RAM). 

## Quick Start

The following examples provide insight on configuration and usage of the role.

### Example inventory file

```yaml
forks:

  vars:

    mavenoVendorIdentifier: <Vendor>
    mavenoForksComponentIdentifier: forks

    mavenoSystemCaCertificatesFilePath: /etc/ssl/certs/ca-certificates.crt

    mavenoManagingLocalBinaryDirectory: "{{ mavenoManagingHomeDirectory }}/.local/bin"

    mavenoPrefixDirectory: "/usr/local/{{ mavenoVendorIdentifier }}"
    mavenoSourceDirectory: "{{ mavenoPrefixDirectory }}/src"
    mavenoLibraryDirectory: "{{ mavenoPrefixDirectory }}/lib"
    mavenoLibrary64Directory: "{{ mavenoPrefixDirectory }}/lib64"
    mavenoBinaryDirectory: "{{ mavenoPrefixDirectory }}/bin"
    mavenoLibexecDirectory: "{{ mavenoPrefixDirectory }}/libexec"
    mavenoSharedDirectory: "{{ mavenoPrefixDirectory }}/share"
    mavenoSystemServiceDirectory: /etc/systemd/system

    mavenoVariableDirectory: /var/local/{{ mavenoVendorIdentifier }}/lib

    mavenoSystemPythonInterpreter: /usr/bin/python3
    mavenoVenvInterpreter: /usr/local/{{ mavenoVendorIdentifier }}/share/{{ mavenoVendorIdentifier }}.venv/bin/python

    mavenoPublicSshKeys:
      - name: 'SSH public key 1'
        sshkey: 'ssh-rsa <...> SSH public key 1'
      - name: 'SSH public key 2'
        sshkey: 'ssh-ed25519 <...> SSH public key 2'
      - ...

  hosts:

    #NOTE: Farmer nodes must be defined before harvester nodes
    <Hostname node1>:

      mavenoManagingSystemUsername: <Managing account username>
      mavenoManagingHomeDirectory: <Managing account home directory>

      mavenoSystemArchitecture: arm64 # amd64|arm64
      mavenoHostDomainName: <Node1 domain name>
      mavenoJobTimeFactor: 4

      mavenoForksBackupDataDirectory: <Blockchains local backup directory>
      mavenoForksBackupHour: 8
      mavenoForksBackupMinute: 0
      mavenoForksBackupWeekday: 0 # Sunday=0, Monday=1, ...

      mavenoForksBuildRequirementsDescriptor:

        chia:
          buildOption: git
          repositoryIdentifier: Chia-Network/chia-blockchain
          nodePort: 8444
          farmerPort: 8447
          startOption: fullnode+farmer
          lightFullNode: yes
          updateHour: 5
          updateMinute: 0
          backup: yes

        chives:
          buildOption: git
          repositoryIdentifier: HiveProject2021/chives-blockchain
          nodePort: 9699
          #farmerPort: 9647
          startOption: fullnode+farmer
          lightFullNode: yes
          permissionsFix: yes
          updateHour: 5
          updateMinute: 30
          backup: yes

        skynet:
          buildOption: git
          repositoryIdentifier: SkynetNetwork/skynet-blockchain
          nodePort: 9999
          #farmerPort: 9998
          buildEnvVars:
            BUILD_VDF_CLIENT: 'N' 
            BUILD_VDF_BENCH: 'N'
          aptPackages:
            - libgmp3-dev
            - libboost-all-dev
          startOption: fullnode+farmer
          lightFullNode: yes
          updateHour: 7
          updateMinute: 0
          backup: yes

        hddcoin:
          buildOption: git
          repositoryIdentifier: HDDcoin-Network/hddcoin-blockchain
          alias: hdd
          systemUsername: hdd
          nodePort: 28444
          #farmerPort: 28447
          startOption: fullnode+farmer
          lightFullNode: yes
          updateHour: 7
          updateMinute: 15
          backup: yes

        silicoin:
          buildOption: git
          repositoryIdentifier: maveno-de/silicoin-blockchain
          branch: v1.1.3
          alias: sit
          executableName: sit
          configurationDirectoryName: .sit
          nodePort: 22222
          farmerPort: 11447
          startOption: fullnode+farmer
          lightFullNode: yes
          updateHour: 5
          updateMinute: 45
          backup: yes


    <Hostname node2>:

      mavenoManagingSystemUsername: <Node2 managing account username>
      mavenoManagingHomeDirectory: <Node2 managing account home directory>

      mavenoSystemArchitecture: arm64 # amd64|arm64
      mavenoHostDomainName: <Node2 domain name>
      mavenoJobTimeFactor: 4

      mavenoForksBuildRequirementsDescriptor:

        chia:
          buildOption: docker
          updateHour: 5
          updateMinute: 0
          instances:
            - name: f0
              startOption: harvester
              farmerAddress: <Farmer domain name>
              farmerPort: 8447
              plotDirectories:
                - <Plots path1>
                - <Plots path2>
                - ...

        silicoin:
          buildOption: docker
          alias: sit
          executableName: sit
          branch: v1.1.3
          updateHour: 5
          updateMinute: 45
          instances:
            - name: f0
              startOption: harvester
              farmerAddress: <Farmer domain name>
              farmerPort: 11447
              plotDirectories:
                - <Plots path1>
                - <Plots path2>
                - ...


    <Hostname node3>:

      mavenoManagingSystemUsername: <Node3 managing account username>
      mavenoManagingHomeDirectory: <Node3 managing account home directory>

      mavenoSystemArchitecture: amd64
      mavenoJobTimeFactor: 1

      mavenoForksBuildRequirementsDescriptor:

        chia:
          buildOption: docker
          nodePort: 8444
          #nodeRpcPort: 8555
          farmerPort: 8447
          fullnodeName: wallet1
          lightFullNode: yes
          updateHour: 5
          updateMinute: 0
          instances:
            - name: wallet1
              startOption: fullnode+wallet
            - name: wallet2
              startOption: wallet

        chives:
          buildOption: docker
          alias: chives
          nodePort: 9699
          #nodeRpcPort: 9755
          farmerPort: 9647
          fullnodeName: wallet1
          lightFullNode: yes
          updateHour: 5
          updateMinute: 30
          instances:
            - name: wallet1
              startOption: fullnode+wallet
            - name: wallet2
              startOption: wallet

        silicoin:
          buildOption: docker
          alias: sit
          nodePort: 28444
          #nodeRpcPort: 28555
          farmerPort: 28447
          fullnodeName: wallet1
          lightFullNode: yes
          updateHour: 7
          updateMinute: 15
          instances:
            - name: wallet1
              startOption: fullnode+wallet
            - name: wallet1
              startOption: wallet

```

### Example Playbook

This is a basic playbook for the application of the role.

```yaml
---

- name: Build Chia Forks
  hosts: forks
  remote_user: "{{ mavenoManagingSystemUsername }}"
  gather_facts: yes
  tasks:

    - name: Switch to Python virtual environment of framework service
      set_fact:
        ansible_python_interpreter: "{{ mavenoVenvInterpreter }}"
      tags:
        - utilities
        - services
        - certificates

    - name: Build Chia Forks
      include_role:
        name: maveno-forks
      tags:
        - utilities
        - services
        - certificates

...
```

### Example command lines

The complete run will install and/or upgrade all configured nodes and additional tools.

```bash
ansible-playbook -i inventory.yml --ask-vault-password playbook.yml
```

Run for selected nodes:

[More on limits](https://docs.ansible.com/ansible/latest/user_guide/intro_patterns.html)


```bash
ansible-playbook -i inventory.yml --limit "node1,node2" --ask-vault-password playbook.yml
```

Run only subtasks. This example will update all certificates on depending harvester type nodes. 

```bash
ansible-playbook -i inventory.yml --tags certificates --ask-vault-password playbook.yml
```

## Subtasks (Tags)

Subtasks are performed during a full deployment but can be executed separately for configuration changes or to update tools deployed with the nodes. Execution of subtasks is controlled with ansible tags.

### utilities

Installation of the following tools for git type nodes:

* Kubec's Chia log analyzer
* Qwinns Forktools

### services

Following services are configured for each node:

* Automatic update
* Automatic backup of blockchain databases (not implemented yet)
* Flora dev-cli (fd-dev-cli) for claiming NFT reward shares (not implemented yet)

### certificates

CA certs of fullnodes are deployed to every harvesters followed by the creation of client certs by each harvester ensuring working connections for any distributed farmer-harvester setups.

## Configuration

Configuration is done by the mavenoForksBuildRequirementsDescriptor variable on a per host basis. This variable can be placed on the inventory file as well as in any group, host or else configuration file following the [ansible framework directory schema](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#ansible-variable-precedence).

mavenoForksBuildRequirementsDescriptor needs to contain a hash which keys are used as fork identifier, eg: chia, flax, etc. Entries on this hash determine which forks are to be installed on the corresponding host. Fork entries itself are hashes that define which instances or the corresponding fork are to be installed. Keys used in fork entries are explained in the following.

### Mandatory parameters

#### buildOption

Type: string \
Values: git, docker \

The build option basically defines the type of deployment that is applied to the node. There can be one git deployment and multiple docker instances on every node. Both build options have their own set of mandatory parameters.

#### startOption

Type: string \
Values: \
fullnode+farmer \
fullnode+wallet \
wallet \
harvester

This defines the type of the deployed node. Nodes of type wallet and harvester cannot be deployed independently from a node of type fullnode+farmer by this role. The start option is translated to Chia command line start options in the deployment, e.g. fullnode+farmer -> farmer, wallet -> wallet-only.

### Mandatory parameters for build option git

#### repositoryIdentifier

Type: string \
Value: The significant part of the URL of the corresponding github repository, e.g.: Chia-Network/chia-blockchain

#### updateHour and updateMinute

Type: integer
Values: Defining time of the day an update is performed after release of a new version.

#### nodePort (only fullnode)

Type: integer
Value: Listening port to be used by the fullnode instance.

#### farmerPort (only farmer and harvester)

Type: integer
Value: Defining listening port for farmers and target port for harvesters.

### Optional parameters (only fullnode)

#### backup

Type: bool
Value: Enables a weekly backup of node and/or wallet blockchain db files to a local directory.

#### systemUsername

Type: string
Value: System username the fork node is using
Default: \<Fork identifier\>

#### alias

Type: string
Value: Command to be used to address the fork executable from managing user account.
Default: \<Fork identifier\>

This could for example be used to address forks from the command line like so:

```bash
xch wallet show
xfx wallet show
...
```
#### executableName

Type: string
Value: Set the executable name of the fork used by the deployment.
Default: \<Fork identifier\>

Some forks use different names for executable and directory prefix, e.g. silicoin-blockchain and sit for the executable.

#### lightFullNode (affects only fullnode type nodes)

Type: bool
Value: When set to true reduced connections limits are configured to reduce CPU and RAM consumption. More forks can be run simultaneously this way.

### Optional parameters for build option git

#### branch

Type: string
Value: Value is passed to the git command as branch name.
Default: main

#### configurationDirectoryName

Type: string
Value: Set the configuration directory name of the fork used by the deployment.
Default: .\<Fork identifier\>

Some forks use different names for config directory and directory prefix, e.g. silicoin-blockchain and .sit for the config directory.

#### buildEnvVars (affects only git type deployments)

Type: List of strings
Value: Additional environment variables passed to the build process

#### aptPackages

Type: List of strings
Value: Additional APT packages to be installed before deployment of a node.

### Mandatory parameters for build option docker

#### fullnodeName

Type: List of strings
Value: The node defined here will be set as target for additional harvester type nodes.

The passed node name must match the name of one of the defined instances. The targetted instance needs to be of type fullnode.

### Optional parameters for build option docker

#### alias

Type: string
Value: Command to be used to address the instance executable from managing user account.
Default: \<Fork identifier\>

This could for example be used to address forks from the command line like so:

```bash
chia-wallet1 wallet show
chia-wallet2 wallet show
flax-wallet1 wallet show
flax-wallet2 wallet show

#in general:
<forkIdentifier or alias>-<instance name> <command parameters> ...
...
```
#### lightFullNode

Type: bool
Value: When set to true reduced connections limits are configured to reduce CPU and RAM consumption. More forks can be run simultaneously this way.

#### instances

Type: List of hashes
Value: A list of fork instances deployed each in a separate docker container.

### Mandatory parameters for docker instance entries

#### name

Type: string
Value: Reference used as part of the instance identifier.

### Mandatory parameters for docker instance entries of type harvester

#### farmerAddress

Type: string
Value: Domain name of the farmer node this harvester connects to.

#### farmerPort

Type: integer
Value: Port of the farmer node this harvester connects to.

### Optional parameters for docker instance entries of type harvester

#### plotDirectories

Type: List of strings
Value: Paths defined in this array are configured for the harvester container during deployment.

Paths defined here needs to exist on the host system and be accessible and readable by the system user designated running the node.

## Credentials preparation

### Vault password

First a good quality vault password should be selected or generated with random number generator. This vault password should then be stored in a password manageger, e.g. KeePass and printed on paper stored in a secure location, e.g. together with your certification of birth.

A good quality password has a minimum length of 24 characters and consists of at least the set of lower and upper case latin characters and numbers [a-zA-Z0-9] while each character has equal probability to appear for each characters of the password producing something similar to this string containing no predictable pattern: RhelhrCCk4l...

A password of 48 random characters of this set are equal to about the security level of a 24-word BIP39 mnemonic seed that Chia uses.

Complying to this requirement the created vault files may be stored in lesser secure places or even publicly, e.g. github repository, without worrying about the contained mnemonics to be compromised.

Store the vault password in a .yml file in a file in a subdirectory of this with path: files/credentials/\<Vendor\>.yml. \<Vendor\> needs to match the string stored in configuration variable mavenoVendorIdentifier. The data contained in the file needs to include this structure:

```yaml
vault:
  password: <Vault password>
```

After this encrypt the file with:

```bash
ansible-vault encrypt files/credentials/<Vendor>.yml
```

The file is now safely encrypted, check with a file editor. Proceed accordingly for every file containing mnemonic seeds using the same \<Vault password\>.

## Mnemonics

Mnemonics for git type deployments are required to contain a structure matching the following:

```yml
forks:
  chia:
    mnemonics: <Mnemonic seed>
```

When running multiple forks to farm a set of plots concurrently the properties of YAML can be used to place references on nodes making it possible store each seed only once. In the following examples all forks except Chives are using the seed used for Chia:


```yml
forks:
  chia: &id001
    mnemonics: <Chia Mnemonics>
  flax: *id001
  chives: <Chives Mnemonics>
    mnemonics: 
  skynet: *id001
  hddcoin: *id001
  silicoin: *id001
```

Mnemnonics for docker type deployments are defined this way:

```yml
forks:
  chia:
    instances:
      - name: wallet1
        mnemonics: <Wallet1 Mnemonics>
      - name: wallet2
        mnemonics: <Wallet2 Mnemonics>

```

Mixing one git type and multiple docker type nodes should work. Harvesters dont need a mnemonics file anyways.
