# Build stage
FROM maven:3.9-amazoncorretto-23 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src

# Build the application
RUN mvn clean package -DskipTests

# Run stage
FROM amazoncorretto:23-alpine
WORKDIR /app

# Copy the built jar from build stage
COPY --from=build /app/target/*.jar app.jar

# Create a directory for external config
RUN mkdir /config

# Copy application.properties to config directory
COPY src/main/resources/application.properties /config/

# Environment variables with defaults
ENV SPRING_PROFILES_ACTIVE=prod \
    SERVER_PORT=8080 \
    DB_URL=jdbc:postgresql://localhost:5432/mydb \
    DB_USERNAME=user \
    DB_PASSWORD=password

# Expose the port
EXPOSE ${SERVER_PORT}

# Run the application with external config and Java 23 specific flags
CMD ["sh", "-c", "java --enable-preview -jar app.jar --spring.config.location=file:/config/application.properties"]