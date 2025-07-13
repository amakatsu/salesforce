package org.openapitools.service;

import org.openapitools.mapper.UserMapper;
import org.openapitools.model.User;
import org.openapitools.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private UserMapper userMapper;

    public List<User> findAllUsers() {
        return userMapper.findAll();
    }

    public User findUserById(long id) {
        return userRepository.findById(id);
    }
}
