class FillingNotFoundException(Exception):
	def __init__(self, filling_id: int):
		self.filling_id = filling_id
		super().__init__(f"Filling with ID {filling_id} not found")
