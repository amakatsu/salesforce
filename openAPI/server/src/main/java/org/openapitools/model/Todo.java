package org.openapitools.model;

import java.net.URI;
import java.util.Objects;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonCreator;
import org.openapitools.jackson.nullable.JsonNullable;
import java.time.OffsetDateTime;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import io.swagger.v3.oas.annotations.media.Schema;

import java.util.*;
import jakarta.annotation.Generated;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/**
 * Todo
 */
@Entity
@Table(name = "todos")
@Generated(value = "org.openapitools.codegen.languages.SpringCodegen", date = "2025-07-13T05:48:33.758880705Z[UTC]", comments = "Generator version: 7.5.0")
public class Todo {

    @Id
    @GeneratedValue
    private Integer id;

    private String text;

    private Boolean done;

    public Todo id(Integer id) {
        this.id = id;
        return this;
    }

    /**
     * Get id
     * 
     * @return id
     */

    @Schema(name = "id", example = "1", requiredMode = Schema.RequiredMode.NOT_REQUIRED)
    @JsonProperty("id")
    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Todo text(String text) {
        this.text = text;
        return this;
    }

    /**
     * Get text
     * 
     * @return text
     */

    @Schema(name = "text", example = "牛乳を買う", requiredMode = Schema.RequiredMode.NOT_REQUIRED)
    @JsonProperty("text")
    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }

    public Todo done(Boolean done) {
        this.done = done;
        return this;
    }

    /**
     * Get done
     * 
     * @return done
     */

    @Schema(name = "done", example = "false", requiredMode = Schema.RequiredMode.NOT_REQUIRED)
    @JsonProperty("done")
    public Boolean getDone() {
        return done;
    }

    public void setDone(Boolean done) {
        this.done = done;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (o == null || getClass() != o.getClass()) {
            return false;
        }
        Todo todo = (Todo) o;
        return Objects.equals(this.id, todo.id) &&
                Objects.equals(this.text, todo.text) &&
                Objects.equals(this.done, todo.done);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, text, done);
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("class Todo {\n");
        sb.append("    id: ").append(toIndentedString(id)).append("\n");
        sb.append("    text: ").append(toIndentedString(text)).append("\n");
        sb.append("    done: ").append(toIndentedString(done)).append("\n");
        sb.append("}");
        return sb.toString();
    }

    /**
     * Convert the given object to string with each line indented by 4 spaces
     * (except the first line).
     */
    private String toIndentedString(Object o) {
        if (o == null) {
            return "null";
        }
        return o.toString().replace("\n", "\n    ");
    }
}
