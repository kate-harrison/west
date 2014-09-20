import custom_logging

print("*** You should see a warning:")
custom_logging.base_logger.warn("This is a sample warning")

new_logger = custom_logging.getModuleLogger("testModule")
print("*** You should see some information from the module testModule:")
new_logger.info("This is some information")
