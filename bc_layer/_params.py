""" ECC parameters """
ecc_curves = [
    "secp256r1",
    "secp384r1",
    "secp521r1",
    "Brainpool-p256r1",
    "Brainpool-p384r1",
    "Brainpool-p512r1"
] # a kind of ecc curves
ecc_curve_default = ecc_curves[0] # first curve is default curve

""" blockchain parameters """
max_block_size = 65536          # 64 KB = 65,536 bytes
max_tx_in_block = 1             # For one block, maybe 120~130 tx can be inserted
genesis_block_seed = "@"        # Seed to generate the prev_hash in the genesis block (promised)
fault_factor = 2/3