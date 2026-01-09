import pandas as pd
import matplotlib.pyplot as plt

# Sample data
data = {
    "Course": ["Python", "Java", "Data Science", "Cloud Computing"],
    "Rating": [4.5, 4.2, 4.8, 4.1]
}

df = pd.DataFrame(data)

# Display data
print(df)

# Plot ratings
plt.bar(df["Course"], df["Rating"])
plt.xlabel("Course Name")
plt.ylabel("Average Rating")
plt.title("Course Rating Analysis")
plt.show()