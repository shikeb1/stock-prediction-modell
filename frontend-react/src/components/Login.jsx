import React, {useContext, useState} from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSpinner } from '@fortawesome/free-solid-svg-icons'

import {useNavigate} from 'react-router-dom'
import { AuthContext } from '../AuthProvider'
import axiosInstance from '../axiosinstance'

const Login = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const [error, setError] = useState('')
  const {isLoggedIn, setIsLoggedIn} = useContext(AuthContext)

 const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    
   try {
     
        const response = await axiosInstance.post('token/', {
          username,
          password
        })
    
    localStorage.setItem('accessToken', response.data.access);
    localStorage.setItem('refreshToken', response.data.refresh);
    console.log('Login successful');
    // Comment out setIsLoggedIn temporarily
     setIsLoggedIn(true);  
    navigate('/dashboard');
    
} catch(error) {
    console.error(error.response?.data);  // ← Show real error
    setError('Invalid credentials');
}
}

  return (
    <>
    <div className='container'>
        <div className="row justify-content-center">
            <div className="col-md-6 bg-light-dark p-5 rounded">
                <h3 className='text-light text-center mb-4'>Login to our Portal</h3>
                <form onSubmit={handleLogin}>
                  <div className='mb-3'>
                    <input type="text" className='form-control' placeholder='Username' value={username} onChange={(e) => setUsername(e.target.value)} />
                  </div>
                    
                    <div className='mb-3'>
                    <input type="password" className='form-control ' placeholder='Set password' value={password} onChange={(e) => setPassword(e.target.value)} />
                    </div>
                    
                    {error && <div className='text-danger'>{error}</div> }

                    {loading ? (
                      <button type='submit' className='btn btn-info d-block mx-auto' disabled><FontAwesomeIcon icon={faSpinner} spin /> Logging in...</button>
                    ) : (
                      <button type='submit' className='btn btn-info d-block mx-auto'>Login</button>
                    )}
                    
                </form>
            </div>
        </div>
    </div>
    </>
  )
}

export default Login