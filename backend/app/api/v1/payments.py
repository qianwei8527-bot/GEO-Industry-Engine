from fastapi import APIRouter
router=APIRouter(prefix='/api/v1/payments',tags=['payments'])
@router.get('/config')
async def get_payment_config():
    import yaml,os;path=os.path.join(os.getcwd(),'config','pricing','payment.yaml')
    with open(path,'r',encoding='utf-8') as f:return yaml.safe_load(f)