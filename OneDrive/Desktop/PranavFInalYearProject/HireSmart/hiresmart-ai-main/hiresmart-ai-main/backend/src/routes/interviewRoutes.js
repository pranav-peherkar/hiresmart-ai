const router=require('express').Router(),axios=require('axios');const AI=process.env.AI_SERVICE_URL||'http://127.0.0.1:8000';
router.post('/questions',async(req,res)=>{try{const r=await axios.post(AI+'/interview/questions',req.body);res.json(r.data)}catch(e){res.status(500).json({message:'Question generation failed'})}});
router.post('/evaluate',async(req,res)=>{try{const r=await axios.post(AI+'/interview/evaluate',req.body);res.json(r.data)}catch(e){res.status(500).json({message:'Evaluation failed'})}});
module.exports=router;
