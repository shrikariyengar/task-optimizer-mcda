import streamlit as st

st.set_page_config(
    page_title = "Task Optimizer", 
    layout = "wide",
    initial_sidebar_state = "expanded"
)

st.markdown(
    """
    <style>
    label p, .stWidgetLabel p {
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        color: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html = True 
)

#normalize function that constrains alll values to a 0 to 1 scale
def normalize(val, min_val, max_val, inverse = False):
    if max_val == min_val:
        return 1.0
    #Formula for min-max constraints
    normal = (val - min_val) / (max_val - min_val)
    if inverse == True:
        return 1.0 - normal

    return normal


#Class to actually take in calculations and do (different object will be created, so the final score will be returned)
class Task:
  #Will ask for the task name, difficulty, days until due, etc. Parameters will be the user inputted weights (converted later)
  def __init__(self, name, due_date, difficulty, time, impact):
    self.task_name = name
    self.task_due_date = due_date
    self.task_difficulty = difficulty
    self.task_time = time
    self.task_impact = impact

  #User input to actually get the user's information about each task


  def calculatePriority(self, w_due_date, w_difficulty, w_time, w_impact, min_time, max_time, min_due_date, max_due_date):

    norm_difficulty = self.task_difficulty / 10.0
    norm_impact = self.task_impact / 10.0

    norm_time = normalize(self.task_time, min_time, max_time, inverse = True)
    norm_due_date = normalize(self.task_due_date, min_due_date, max_due_date, inverse = True)
    #days = self.task_due_date if self.task_due_date > 0 else 0.1
    priority_calculation = (
    (w_due_date * norm_due_date) 
    + (w_difficulty * norm_difficulty) 
    + (w_time * norm_time) 
    + (w_impact * norm_impact)
    )
    return priority_calculation

#allTasks will start as a blank list and will have new objects appended to it through each iteration
def main():
    st.title("Task Optimizer")
    st.markdown("Welcome to Task Optimizer. Before, you begin inputting your tasks, please take a moment and answer the questions below: ")
    
    with st.container(border = True):
        st.markdown("### Adjusting Weights/Importance")
        st.caption("NOTE: THESE SELECTIONS WILL INFLUENCE CALCULATIONS AND THE ORDER OF IMPORTANCE: TO UPDATE THESE, PLEASE TYPE 'change' AT ANY POINT")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        w_date = st.selectbox("Would you like the due date to be low, medium, high, or of critical importance? ", ["LOW","MEDIUM","HIGH","CRITICAL"])

    with col2:
        w_difficulty = st.selectbox("Would you like the difficulty to be low, medium, high, or of critical importance? ", ["LOW","MEDIUM","HIGH","CRITICAL"])

    with col3:
        w_time = st.selectbox("Would you like the time left to be low, medium, high, or of critical importance? ", ["LOW","MEDIUM","HIGH","CRITICAL"])
    
    with col4:
        w_impact = st.selectbox("Would you like the impact it will have on your grades to be low, medium, high, or of critical importance? ", ["LOW","MEDIUM","HIGH","CRITICAL"])

    weightedList = [w_date, w_difficulty, w_time, w_impact]
    for weight in range(len(weightedList)):
        if (weightedList[weight].upper() == "LOW"):
            weightedList[weight] = 0.15

        elif (weightedList[weight].upper() == "MEDIUM"):
            weightedList[weight] = 0.45

        elif (weightedList[weight].upper() == "HIGH"):
            weightedList[weight] = 0.65

        elif (weightedList[weight].upper() == "CRITICAL"):
            weightedList[weight] = 0.90
        else:
            weightedList[weight] = 0.50

    w_date, w_difficulty, w_time, w_impact = weightedList
    allTasks = []

    st.markdown("### Task/Assignment Entries")
    st.caption("These inputs will be used from now unless you are to change the values. Now we will begin the Task Input")
    taskNum = st.number_input("How many tasks do you have?", min_value = 1, value = 2, step = 1)

    #Allows user to fully type inputs
    with st.form("task_input_form"):
        for i in range(int(taskNum)):
            st.write(f"---Task {i + 1} ---")
            st.write()
            #Get the actual inputs
            column1, column2, column3, column4, column5 = st.columns(5)
            
            with column1:
                t_name = st.text_input("Enter the task name: " , key = f"name_{i}")
            
            with column2:
                t_due_date = st.number_input("How many days until it is due? ",  key = f"due_{i}", min_value = 1, value = 5, step = 1)
            
            with column3:
                t_difficulty = st.number_input("How difficult is this task, on a scale of 1-10? " ,  key = f"difficulty_{i}", min_value = 1, value = 5, max_value = 10, step = 1)
            
            with column4:
                t_time = st.number_input("How long will this realistically take, in minutes? ", key = f"time_{i}", min_value = 10, value = 30, step = 15)
           
            with column5:
                t_impact = st.number_input("What impact will this assignment/task have on your grades, on a scale of 1-10", key = f"impact_{i}", min_value = 1, value = 5, max_value = 10, step = 1)


            task = Task(t_name, t_due_date, t_difficulty, t_time, t_impact)
            #Append task to the list allTasks
            allTasks.append(task)

        submit_button = st.form_submit_button("Calculate Optimal Order To Complete", use_container_width = True)

    #The plan was to append the tasks to the list, and then we run through the list, see which are highest, and print from highest to lowest score
    #Use .sort reverse method to print from highest to lowest values
    if submit_button:
        st.markdown("-----Your Priority Schedule-----")
        all_times = [t.task_time for t in allTasks]
        all_due_dates = [t.task_due_date for t in allTasks]

        min_time = min(all_times)
        max_time = max(all_times)

        min_due_date = min(all_due_dates)
        max_due_date = max(all_due_dates)
        

        allTasks.sort(key = lambda taskObject: taskObject.calculatePriority(w_date, w_difficulty, w_time, w_impact, min_time, max_time, min_due_date, max_due_date), reverse = True)
        for i in range(len(allTasks)):
            currentTask = allTasks[i]
            score =  currentTask.calculatePriority(w_date, w_difficulty, w_time, w_impact, min_time, max_time, min_due_date, max_due_date)
            st.success(f"Number {i+1}: {currentTask.task_name} --- Priority Score: {score:.2f}")
        

if __name__ == "__main__":
    main()

st.write("HI")
st.write("Bye")


#To run
#python3 -m streamlit run main.py

#To update changes: 
"""git add .
git commit -m "Describe your changes here"
git push origin main"""