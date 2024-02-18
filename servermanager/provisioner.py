# Set up / tear down the linode

# Standup steps:
# 1. Call linode API to provision linode
# 2. Wait for linode to be ready
# 3. Rsync server files
# 4. Run entry point
# 5. Check server started healthily?

# Shutdown steps:
# 1. Run shutoff script (graceful shutdown of server)
# 2. Rsync files back to local directory
# 3. Linode API to delete linode
