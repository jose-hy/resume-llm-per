package com.example.resume_matching_analytics.Auth.controller;

import com.example.resume_matching_analytics.Auth.model.User;
import com.example.resume_matching_analytics.Auth.service.UserService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseCookie;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class UserController {
    @Autowired
    private final UserService service;

    public UserController(UserService service) {
        this.service = service;
    }

    @PostMapping("/register")
    public void register(@RequestBody User user, HttpServletResponse response) {
        String token = service.register(user);
        String env = System.getProperty("env");

        ResponseCookie cookie = ResponseCookie.from("accessCode", token)
                .maxAge(60 * 60 * 1000)
                .sameSite("Strict")
                .httpOnly(true)
                .secure(true)
                .path("/")
                .domain(".interviewmoves.org")
                .build();
        response.addHeader(HttpHeaders.SET_COOKIE, cookie.toString());
    }

    @PostMapping("/login")
    public void login(@RequestBody User user, HttpServletResponse response, HttpServletRequest req) {
        String token = service.verify(user);
        String env = System.getProperty("env");
        ResponseCookie cookie = ResponseCookie.from("accessCode", token)
                .maxAge(60 * 60 * 1000)
                .sameSite(env === "development" ? "Lax" : "Strict")
                .httpOnly(true)
                .secure(env !== "development")
//                .secure(true)
                .path("/")
                .domain(env === "development" ? "localhost" : ".interviewmoves.org")
                .build();
        response.addHeader(HttpHeaders.SET_COOKIE, cookie.toString());
    }

    @GetMapping("/logout_user")
    public void logout_user(HttpServletResponse response) {
        ResponseCookie cookie = ResponseCookie.from("accessCode", "")
                .maxAge(0)
                .httpOnly(true)
                .sameSite("Strict")
                .secure(true)
                .path("/")
                .domain(".interviewmoves.org")
                .build();
        response.addHeader(HttpHeaders.SET_COOKIE, cookie.toString());
    }

}
