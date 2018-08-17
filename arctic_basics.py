from arctic import Arctic
import pandas as pd

# Connect to Local MONGODB
store = Arctic('localhost')

# Create the library - defaults to VersionStore
store.initialize_library('TESTE')

# Access the library
library = store['TESTE']

# Create some data
data = pd.DataFrame([1, 2], index=[3, 4], columns=['coluna1'])

# Store the data in the library
library.write('TestData', data)

# List libraries from store
store.list_libraries()

# List symbols from library
library.list_symbols()

# Read back the data
data_readed = library.read('TestData').data

# Delete data from library
library.delete('TestData')

# Delete library
store.delete_library('TESTE')
