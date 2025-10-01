package com.example.resume_matching_analytics.Auth.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
@EnableWebMvc
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**") // Allow CORS for all endpoints
                .allowedOriginPatterns("http://localhost:5173", 
                "https://*.interviewmoves.org", "https://interviewmoves.org/*",
                "https://*.interviewmoves.org/*") // Specify the frontend origin
                .allowedMethods("GET", "POST", "PUT", "DELETE") // Allowed HTTP methods
                .allowCredentials(true) // Allow credentials (cookies)
                .allowedHeaders("*"); // Allow all headers
    }
}
