Provisioners
*******************

`smpsave` is built such that the user can leverage any cloud provider they wish, as long as there is a `Provisioner` class implemented for that provider.
Each `Provisioner` will generally have its own configuration requirements.
At the time of writing, only linode is supported. It serves as an example of how other provisioners may be implemented.

.. autoclass:: smpsave.provisioning.Provisioner
   :members:


Linode
======
.. autoclass:: smpsave.provisioning.LinodeProvisioner
