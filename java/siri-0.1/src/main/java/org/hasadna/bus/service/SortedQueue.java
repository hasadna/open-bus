package org.hasadna.bus.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.PriorityBlockingQueue;
import java.util.function.Function;
import java.util.stream.Collectors;

@Component
public class SortedQueue {

    protected final Logger logger = LoggerFactory.getLogger(SortedQueue.class);

    void put(Command command) {
        queue.offer(command);
    }

    public Command peek() {
        return queue.peek();
    }

    Command takeFromQueue() {
        return queue.poll();
    }

    // beware! this operation takes O(n) and is not accurate
    int size() {
        return queue.size();
    }

    boolean isEmpty() {
        return queue.isEmpty();
    }

    public Command[] getAll() {
        Command data[] = new Command[queue.size()];
        Iterator<Command> iter = queue.iterator();
        int i = 0 ;
        while (iter.hasNext()) {
            data[i++] = iter.next();
        }
        return data;
    }

    public List<String> showAll() {
        return queue.stream().map(c -> c.toString()).collect(Collectors.toList());
    }


    List<Command> removeByLineRef(String lineRef) {
        logger.debug("removing all schedules of lineRef {}", lineRef);
        List<Command> candidatesToRemoval = new ArrayList<>();
        Iterator iter = queue.iterator();
        while (iter.hasNext()) {
            Command current = (Command) iter.next();
            if (current.lineRef.equals(lineRef)) {
                candidatesToRemoval.add(current);
            }
        }
        List<Command> removed = new ArrayList<>();
        for (Command c : candidatesToRemoval) {
            boolean result = queue.remove(c);
            if (result) {
                removed.add(c);
            }
            else {
                logger.warn("removal of {} returned false", c);
            }
        }
        logger.debug("return a list of {} schedules", removed.size());
        logger.trace("return {}", removed);
        return removed;
    }


    private Queue<Command> queue = new PriorityBlockingQueue<>(20, (c1, c2) -> c1.nextExecution.isBefore(c2.nextExecution)?-1:1);

}
