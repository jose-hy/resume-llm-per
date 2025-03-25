package com.example.resume_matching_analytics.Auth.controller;

import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Arrays;

@RestController
public class HelloController {
    @CrossOrigin(origins = "https://interviewmoves.org/", allowCredentials = "true")
    @GetMapping("")
    public String greeting(HttpServletRequest req) {
        return "Working" + req.getSession().getId();
    }
}
