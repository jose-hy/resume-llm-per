package com.example.resume_matching_analytics.Auth.service;

import com.example.resume_matching_analytics.Auth.model.User;
import com.example.resume_matching_analytics.Auth.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class UserService {
    @Autowired
    private final UserRepository repo;

    @Autowired
    private final AuthenticationManager authManager;

    @Autowired
    private JWTService jwtService;

    private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(12);

    public UserService(UserRepository repo, AuthenticationManager authManager) {
        this.repo = repo;
        this.authManager = authManager;
    }

    public String register(User user) {
        user.setPassword(encoder.encode(user.getPassword()));
        repo.save(user);
        return jwtService.generateToken(user.getUsername());
    }

    public String verify(User user) {
        Authentication auth = authManager.authenticate(
                new UsernamePasswordAuthenticationToken(user.getUsername(), user.getPassword())
        );

        if (auth.isAuthenticated()) {
            return jwtService.generateToken(user.getUsername());
        }

        return "Not working";
    }
}

