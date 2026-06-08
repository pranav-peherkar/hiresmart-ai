const router=require('express').Router(),bcrypt=require('bcryptjs'),jwt=require('jsonwebtoken'),User=require('../models/User');
router.post('/register',async(req,res)=>{try{const{name,email,password}=req.body;const hash=await bcrypt.hash(password,10);const u=await User.create({name,email,password:hash});res.json({message:'Registered',user:{id:u._id,name,email}})}catch(e){res.status(400).json({message:e.message})}});
router.post('/login',async(req,res)=>{const{email,password}=req.body;const u=await User.findOne({email});if(!u||!await bcrypt.compare(password,u.password))return res.status(401).json({message:'Invalid credentials'});const token=jwt.sign({id:u._id},process.env.JWT_SECRET||'secret');res.json({token,user:{id:u._id,name:u.name,email:u.email}})});
module.exports=router;
