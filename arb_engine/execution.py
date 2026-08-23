from .models import ExecutionResult
class PaperExecutor:
    async def execute(self,venue,side,symbol,quantity,price):
        return ExecutionResult(venue,side,symbol,quantity,price,0,'paper execution only')
