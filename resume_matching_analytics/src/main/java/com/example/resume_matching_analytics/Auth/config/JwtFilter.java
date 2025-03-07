package com.example.resume_matching_analytics.Auth.config;

import com.example.resume_matching_analytics.Auth.model.CustomUserDetails;
import com.example.resume_matching_analytics.Auth.model.User;
import com.example.resume_matching_analytics.Auth.repository.UserRepository;
import com.example.resume_matching_analytics.Auth.service.JWTService;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

@Component
public class JwtFilter extends OncePerRequestFilter {
    @Autowired
    private JWTService jwtService;

    @Autowired
    UserRepository userRepository;

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {
        List<String> publicEndpoints = List.of("/register", "/login");
        String path = request.getRequestURI();

        if (!publicEndpoints.contains(path)) {
            String token = null;
            String username = null;

            Cookie[] cookies = request.getCookies();
            if (cookies != null) {
                for (Cookie cookie : cookies) {
                    if ("accessCode".equals(cookie.getName())) {
                        token = cookie.getValue();
                        username = jwtService.extractUsername(token);
                    }
                }
            }

            if (SecurityContextHolder.getContext().getAuthentication() == null) {
                User user = userRepository.findByUsername(username);

                if (user == null) {
                    System.out.println("User Not Found");
                    throw new UsernameNotFoundException("user not found");
                }

                CustomUserDetails userDetails = new CustomUserDetails(user);
                if (jwtService.validateToken(token, userDetails)) {
                    UsernamePasswordAuthenticationToken authToken =
                            new UsernamePasswordAuthenticationToken(userDetails, null, userDetails.getAuthorities());
                    authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                    SecurityContextHolder.getContext().setAuthentication(authToken);
                }
            }
        }

        filterChain.doFilter(request, response);
    }
}

